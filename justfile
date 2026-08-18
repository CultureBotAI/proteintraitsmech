# ProteinTraitsMech - protein sequence & structure trait knowledge base

set dotenv-load := true

# ============== Deep Research ==============

research_dir := "research"
templates_dir := "templates"

# Provider-based research for one protein trait path, slug, identifier, or label.
research-protein-trait provider target *args="":
    uv run --extra dev python scripts/research_protein_trait.py \
      --provider {{provider}} --target {{target}} \
      --template {{templates_dir}}/protein_trait_mechanism_research.md \
      --research-dir {{research_dir}} {{args}}

# Raw deep-research-client provider availability/parameter listing.
research-providers:
    uv run --extra dev deep-research-client providers

research-provider provider:
    uv run --extra dev deep-research-client providers --provider {{provider}}

# Rank providers for mechanism or family-grounding work.
deep-research-providers focus="mechanism" *args="":
    uv run --extra dev python scripts/deep_research_provider.py \
      --config conf/deep_research_provider.yaml --focus {{focus}} {{args}}

# Show one provider's focus-specific fit, capabilities, and availability.
deep-research-provider provider focus="mechanism" *args="":
    uv run --extra dev python scripts/deep_research_provider.py \
      --config conf/deep_research_provider.yaml --provider {{provider}} \
      --focus {{focus}} {{args}}

default:
    @just --list --unsorted

# Install package + dev tools
install:
    uv sync --extra dev

# Generate Python dataclasses from LinkML schema
gen-schema:
    uv run gen-pydantic src/proteintraitsmech/schema/proteintraitsmech.yaml > src/proteintraitsmech/schema/proteintraitsmech_dataclasses.py

# Validate a single ProteinTraitRecord YAML against the schema
validate file:
    uv run linkml-validate -s src/proteintraitsmech/schema/proteintraitsmech.yaml \
      --target-class ProteinTraitRecord {{file}}

# Validate every YAML under data/traits/ by invoking the `linkml-validate`
# CLI. Files are batched (default 200) so 18K records finish in ~1-2 min.
# Scope to a subset with a path/glob: just validate-all data/traits/sequence/motif
validate-all *args:
    uv run python scripts/validate_linkml.py {{args}}

# Alias — same runner as validate-all; kept for scripts referencing the
# CLI's name directly.
validate-linkml *args:
    uv run python scripts/validate_linkml.py {{args}}

# Programmatic schema-quality probes
audit-schema:
    uv run python scripts/audit_schema.py

# Unit tests for the pure helpers (scripts/record_io.py and friends). These do NOT
# touch data/traits - `validate-all` and `audit-graphs` are the data gates.
# Run the unit tests
test *args:
    uv run pytest tests/ {{args}}

# Static checks over the Python. Gated at ZERO rather than ratcheted from a baseline:
# the 63 pre-existing errors were all trivial (semicolons, `l` as a variable name,
# unused locals, f-strings without placeholders) and are fixed, so there is no number
# to remember and no reason for the count to be anything but zero. See #107.
# Lint the Python
lint *args:
    uv run ruff check scripts/ tests/ {{args}}

# Cross-checks download.yaml against the seeders; warns on restrictive (NC/ND)
# licences and orphan seeders.
# Validate the data-source registry
sources-check:
    uv run python scripts/check_sources.py

# Structural-integrity audit of causal graphs
audit-graphs *args:
    uv run python scripts/audit_causal_graphs.py {{args}}

# Reports encoding damage by source and kind. Separates REVERSIBLE damage (mojibake, C1
# controls — repair_mojibake undoes these, and a non-zero count exits 1) from U+FFFD,
# which is lossy: the original bytes are gone, so it is reported as a fact rather than a
# failure. See #139.
# Audit text-encoding damage
audit-text *args:
    uv run python scripts/audit_text_quality.py {{args}}

# Audit whether definitions read as prose (#149). Fails on definitions WE composed;
# reports, without failing, the same defects in curator-written source abstracts we
# reproduce faithfully.
audit-prose *args:
    uv run python scripts/audit_prose_quality.py {{args}}

# LLM review of InterPro's unreviewed LLM abstracts (issue #92). Dry-run by default;
# --apply calls the reviewer and appends to data/reviews/. Resumable: a candidate that
# already has a verdict is skipped, so an interrupted run costs only its current batch.
# Run several in parallel with --shard i/n --out <file>.
# Review unpromoted LLM abstracts
review-abstracts *args:
    uv run python scripts/review_llm_abstracts.py review {{args}}

# Applies the PROMOTE verdicts: the abstract becomes `definition`, provenance records
# that it is LLM-generated and LLM-reviewed but NOT curator-reviewed, and the status
# becomes PROPOSED. Deterministic and idempotent - safe to re-run as verdicts arrive.
# Promote reviewed abstracts to definitions
promote-abstracts *args:
    uv run python scripts/review_llm_abstracts.py promote {{args}}

# Review the trait categories each source contributes + flag mis-modelled records
review-categories *args:
    python3 scripts/review_source_categories.py {{args}}

# Seed data/traits/structure/ from the LinkML valuesets LocalStructuralFeature enum.
# Dry-run by default; re-run with --apply to write. Stdlib-only, no uv required.
seed-lsf *args:
    python3 scripts/seed_localstructuralfeature.py {{args}}

# Download the current PROSITE release into data/raw/. The files are
# gitignored — regenerate any time with this recipe.
fetch-prosite:
    mkdir -p data/raw
    curl -sS --fail --max-time 300 -o data/raw/prosite.dat  ftp://ftp.expasy.org/databases/prosite/prosite.dat
    curl -sS --fail --max-time 120 -o data/raw/prorule.dat  ftp://ftp.expasy.org/databases/prosite/prorule.dat
    curl -sS --fail --max-time 300 -o data/raw/prosite.doc  ftp://ftp.expasy.org/databases/prosite/prosite.doc
    curl -sS --fail --max-time  30 -o data/raw/ps_reldt.txt ftp://ftp.expasy.org/databases/prosite/ps_reldt.txt
    @cat data/raw/ps_reldt.txt

# Seed data/traits/ from PROSITE patterns / profiles / ProRules.
# Requires `just fetch-prosite` first. Dry-run by default; --apply to write.
seed-prosite *args:
    python3 scripts/seed_prosite.py {{args}}

# Materialize Pfam clan + PROSITE PDOC grouping nodes (fix dangling parents)
seed-pfam-clans *args:
    python3 scripts/seed_pfam_clans.py {{args}}

seed-prosite-pdoc *args:
    python3 scripts/seed_prosite_pdoc.py {{args}}

# Download the TED (Encyclopedia of Domains) novel + high-symmetry fold
# catalogues from Zenodo (DOI:10.5281/zenodo.13908086, CC-BY 4.0).
fetch-ted:
    mkdir -p data/raw
    curl -sSLf --max-time 300 -o data/raw/ted_novel_folds.tsv.gz \
      https://zenodo.org/records/13908086/files/novel_folds_set.domain_summary.tsv.gz
    curl -sSLf --max-time 300 -o data/raw/ted_high_symmetry_folds.tsv.gz \
      https://zenodo.org/records/13908086/files/high_symmetry_folds_set.domain_summary.tsv.gz
    @ls -la data/raw/ted_*.tsv.gz

# Seed data/traits/structure/fold/ from the TED novel + high-symmetry fold
# catalogues. Requires `just fetch-ted` first. Dry-run by default.
seed-ted *args:
    python3 scripts/seed_ted.py {{args}}

# Seed data/traits/sequence/disorder/ from DisProt (Tosatto lab).
# CC-BY-4.0. First run fetches the full search JSON and caches to
# data/raw/disprot.entries.json; subsequent runs replay the cache.
seed-disprot *args:
    python3 scripts/seed_disprot.py {{args}}

# Seed data/traits/structure/active_site/mcsa/ from M-CSA (Thornton lab,
# EBI). CC-BY-4.0. First run fetches the paginated JSON API and caches
# to data/raw/mcsa.entries.jsonl; subsequent runs replay the cache.
# Dry-run by default; --apply to write.
seed-mcsa *args:
    python3 scripts/seed_mcsa.py {{args}}

# Seed data/traits/structure/{class,fold,homologous_superfamily,domain}/
# from SCOPe (Berkeley SCOP extension). The berkeley.edu server is
# behind an anti-bot challenge that rejects plain HTTP clients — the
# `fetch-scope` recipe will fail; download the files manually from
# https://scop.berkeley.edu/downloads/ (dir.des.scope.*.txt and
# dir.hie.scope.*.txt) and drop them into data/raw/scope/.
seed-scope *args:
    python3 scripts/seed_scope.py {{args}}

# Download the current ECOD domain list (~689 MB) from UT Southwestern.
# The archive is regenerated weekly on PDB sync; every fetch pulls the
# then-current version. Not gitignored yet; add to .gitignore if it
# grows past 1 GB.
fetch-ecod:
    mkdir -p data/raw
    curl -sSLf --max-time 1800 -o data/raw/ecod.latest.domains.txt \
      http://prodata.swmed.edu/ecod/distributions/ecod.latest.domains.txt
    @ls -la data/raw/ecod.latest.domains.txt

# Seed data/traits/structure/{architecture,homologous_superfamily,
# topology,fold/ecod}/ from the ECOD hierarchy. Emits one record per
# distinct A/X/H/T/F node (~20-30K total) with parent_traits chaining
# through the levels. Requires `just fetch-ecod`.
seed-ecod *args:
    python3 scripts/seed_ecod.py {{args}}

# Reactome pathways (CC0) -> FUNC_PATHWAY.
fetch-reactome:
    mkdir -p data/raw/reactome
    curl -sSLf --max-time 120 -o data/raw/reactome/ReactomePathways.txt https://reactome.org/download/current/ReactomePathways.txt
    curl -sSLf --max-time 120 -o data/raw/reactome/ReactomePathwaysRelation.txt https://reactome.org/download/current/ReactomePathwaysRelation.txt

seed-reactome *args:
    python3 scripts/seed_reactome.py {{args}}

fetch-tcdb:
    mkdir -p data/raw/tcdb
    curl -sSLf --max-time 120 -o data/raw/tcdb/families.tsv https://www.tcdb.org/cgi-bin/projectv/public/families.py
    curl -sSLf --max-time 120 -o data/raw/tcdb/substrates.tsv https://www.tcdb.org/cgi-bin/substrates/getSubstrates.py

seed-tcdb *args:
    python3 scripts/seed_tcdb.py {{args}}

# Download the MetalPDB bulk flat file (per-PDB metal sites; CERM, Univ.
# Florence). NO explicit reuse licence — seeded records are flagged; confirm
# terms with CERM before redistribution. ~40 MB gzip, gitignored.
fetch-metalpdb:
    mkdir -p data/raw/metalpdb
    curl -sSLf --max-time 600 -o data/raw/metalpdb/flat_db_file.xml.gz \
      "https://metalpdb.cerm.unifi.it/download?t=flatdb&id=flat_db_file.xml.gz"
    @ls -la data/raw/metalpdb/flat_db_file.xml.gz

# Seed data/traits/structure/metal_site/metalpdb/ — one STRUCT_METAL_SITE class
# per (metal element, nuclearity), aggregated from MetalPDB per-PDB sites.
# Requires `just fetch-metalpdb`. Dry-run by default; --apply to write.
seed-metalpdb *args:
    python3 scripts/seed_metalpdb.py {{args}}

# 3did domain-domain interaction interfaces (IRB Barcelona; no explicit open
# license, FLAGGED) -> STRUCT_INTERFACE. One class per Pfam-pair interface, with
# representative PDBs. Dry-run by default; --apply.
fetch-3did:
    mkdir -p data/raw/3did
    curl -sSLf --max-time 300 -o data/raw/3did/3did_flat.gz https://3did.irbbarcelona.org/download/current/3did_flat.gz
    @ls -la data/raw/3did/3did_flat.gz

seed-3did *args:
    python3 scripts/seed_3did.py {{args}}

# BioLiP2 non-redundant ligand-binding-site flat file + ligand table + readme
# (Yang/Zhang group). Free for academic use, no explicit open license (FLAGGED).
fetch-biolip:
    mkdir -p data/raw/biolip
    curl -sSLf --max-time 300 -o data/raw/biolip/BioLiP_nr.txt.gz https://zhanggroup.org/BioLiP/download/BioLiP_nr.txt.gz
    gunzip -f data/raw/biolip/BioLiP_nr.txt.gz
    curl -sSLf --max-time 300 -o data/raw/biolip/ligand.tsv.gz https://zhanggroup.org/BioLiP/data/ligand.tsv.gz
    gunzip -f data/raw/biolip/ligand.tsv.gz
    curl -sSLf --max-time 60  -o data/raw/biolip/readme.txt https://zhanggroup.org/BioLiP/download/readme.txt
    @wc -l data/raw/biolip/BioLiP_nr.txt data/raw/biolip/ligand.tsv

# Aggregate BioLiP rows into ligand-keyed STRUCT_BINDING_SITE classes.
# Requires `just fetch-biolip` first. Dry-run by default; --apply to write.
seed-biolip *args:
    python3 scripts/seed_biolip.py {{args}}

fetch-cog:
    mkdir -p data/raw/cog
    curl -sSLf --max-time 120 -o data/raw/cog/cog-20.def.tab https://ftp.ncbi.nlm.nih.gov/pub/COG/COG2020/data/cog-20.def.tab
    curl -sSLf --max-time 60 -o data/raw/cog/fun-20.tab https://ftp.ncbi.nlm.nih.gov/pub/COG/COG2020/data/fun-20.tab

seed-cog *args:
    python3 scripts/seed_cog.py {{args}}

# SEED subsystems via BV-BRC subsystem_ref (US Gov public domain) -> FUNC_PATHWAY.
fetch-seed-subsystems:
    mkdir -p data/raw/seed_subsystems
    curl -sSLf --max-time 300 -H "Accept: application/json" -o data/raw/seed_subsystems/subsystem_ref.json "https://www.bv-brc.org/api/subsystem_ref/?limit(25000)&http_accept=application/json"

seed-seed-subsystems *args:
    python3 scripts/seed_seed_subsystems.py {{args}}

fetch-rhea:
    mkdir -p data/raw/rhea
    curl -sSLf --max-time 300 -o data/raw/rhea/rhea-reactions.tsv "https://www.rhea-db.org/rhea?query=&columns=rhea-id,equation,chebi-id,ec&format=tsv"

seed-rhea *args:
    python3 scripts/seed_rhea.py {{args}}

fetch-ec:
    mkdir -p data/raw/ec
    curl -sSLf --max-time 120 -o data/raw/ec/enzyme.dat https://ftp.expasy.org/databases/enzyme/enzyme.dat
    curl -sSLf --max-time 60 -o data/raw/ec/enzclass.txt https://ftp.expasy.org/databases/enzyme/enzclass.txt

seed-ec *args:
    python3 scripts/seed_ec.py {{args}}

fetch-chebi:
    mkdir -p data/raw/chebi
    curl -sSLf --max-time 300 -o data/raw/chebi/compounds.tsv.gz https://ftp.ebi.ac.uk/pub/databases/chebi/flat_files/compounds.tsv.gz
    curl -sSLf --max-time 300 -o data/raw/chebi/chemical_data.tsv.gz https://ftp.ebi.ac.uk/pub/databases/chebi/flat_files/chemical_data.tsv.gz
    curl -sSLf --max-time 600 -o data/raw/chebi/structures.tsv.gz https://ftp.ebi.ac.uk/pub/databases/chebi/flat_files/structures.tsv.gz
    # relation.tsv.gz (is_a / has_role edges) drives the cofactor role subtree
    curl -sSLf --max-time 300 -o data/raw/chebi/relation.tsv.gz https://ftp.ebi.ac.uk/pub/databases/chebi/flat_files/relation.tsv.gz

# Build docs/data/chebi.json (name/formula/InChIKey for referenced ChEBI ids)
build-chebi:
    python3 scripts/build_chebi_sidecar.py

# Seed cofactor-requirement traits from the ChEBI `cofactor` role subtree
# (CHEBI:23357) -> FUNC_COFACTOR_REQUIREMENT. Requires `just fetch-chebi`.
# Then align with the sibling projects' cofactor vocabularies (MicroGrowAgents +
# PFAS) and write data/mappings/cofactor_crosswalk.tsv. Dry-run by default.
seed-cofactor *args:
    python3 scripts/seed_chebi_cofactor.py {{args}}
    python3 scripts/seed_cofactor_alignment.py {{args}}

# Curated stable complexes from the EBI Complex Portal (CC0, per-species
# ComplexTAB) -> FUNC_INTERACTION_PARTNER (members as has_part edges).
fetch-complexportal:
    mkdir -p data/raw/complexportal
    base=https://ftp.ebi.ac.uk/pub/databases/intact/complex/current/complextab; \
    for f in $(curl -sSLf --max-time 60 $base/ | grep -oE '[0-9_a-z]+\.tsv'); do \
      curl -sSLf --max-time 60 -o data/raw/complexportal/$f $base/$f; done
    @ls data/raw/complexportal/*.tsv | wc -l

seed-complexportal *args:
    python3 scripts/seed_complexportal.py {{args}}

# --- Round-4 sources (research/protein-trait-sources-round4.md) ---

# UniProtKB controlled-vocabulary Keywords (CC-BY 4.0) -> class-level
# FUNC_BINDING_CAPACITY (Ligand) / FUNC_ENVIRONMENTAL_RESPONSE / SEQ_TARGETING_SIGNAL.
fetch-uniprot-keywords:
    mkdir -p data/raw/uniprot_keywords
    curl -sSLf --max-time 120 -o data/raw/uniprot_keywords/keywlist.txt \
      https://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/docs/keywlist.txt
    @wc -l data/raw/uniprot_keywords/keywlist.txt

seed-uniprot-keywords *args:
    python3 scripts/seed_uniprot_keywords.py {{args}}

# OPM membrane-protein classification (CC-BY 3.0) -> MIXED_TRANSMEMBRANE / STRUCT_CLASS.
# Fetches the OPM REST backend JSON (types + per-classtype detail with nested
# superfamilies). Seeds the classification terms, not the per-PDB instances.
fetch-opm:
    mkdir -p data/raw/opm
    base=https://opm-back.cc.lehigh.edu/opm-backend; \
    curl -sSLf --max-time 30 -o data/raw/opm/types.json "$base/types"; \
    curl -sSLf --max-time 30 -o data/raw/opm/classtypes.json "$base/classtypes?pageSize=50"; \
    for id in $(python3 -c "import json;print(' '.join(str(o['id']) for o in json.load(open('data/raw/opm/classtypes.json'))['objects']))"); do \
      curl -sSLf --max-time 30 -o data/raw/opm/classtype_$id.json "$base/classtypes/$id"; done
    @ls data/raw/opm/classtype_*.json | wc -l

seed-opm *args:
    python3 scripts/seed_opm.py {{args}}

# OrthoDB v12 orthologous groups (CC-BY 4.0) -> FUNC_ORTHOLOG_GROUP. Scoped by
# --level (default broad domain clades) + capped (--limit); the OGs table is ~128 MB.
fetch-orthodb:
    mkdir -p data/raw/orthodb
    base=https://data.orthodb.org/v12/download/odb_data_dump; \
    curl -sSLf --max-time 600 -o data/raw/orthodb/odb12v2_OGs.tab.gz "$base/odb12v2_OGs.tab.gz"; \
    curl -sSLf --max-time 60  -o data/raw/orthodb/odb12v2_levels.tab.gz "$base/odb12v2_levels.tab.gz"
    @ls -la data/raw/orthodb/*.gz

seed-orthodb *args:
    python3 scripts/seed_orthodb.py {{args}}

# OMA hierarchical orthologous groups (CC-BY 4.0) -> FUNC_ORTHOLOG_GROUP. The
# seeder pages the OMA REST API (level-scoped, named HOGs) and caches to
# data/raw/oma/; no separate fetch step. Overlaps OrthoDB (downstream dedup).
seed-oma *args:
    python3 scripts/seed_oma.py {{args}}

# IEDB linear-peptide epitopes (CC-BY 4.0) -> SEQ_EPITOPE. Aggregates the
# ~2M-row epitope export (1 GB) to UniProt-grounded epitope classes, capped.
fetch-iedb:
    mkdir -p data/raw/iedb
    curl -sSLf --max-time 300 -o data/raw/iedb/epitope_full_v3.zip \
      "https://www.iedb.org/downloader.php?file_name=doc/epitope_full_v3.zip"
    cd data/raw/iedb && unzip -o -q epitope_full_v3.zip
    @ls -la data/raw/iedb/epitope_full_v3.csv

seed-iedb *args:
    python3 scripts/seed_iedb.py {{args}}

# Validate data/methods/methods.yaml + build docs/data/methods.json (detection methods)
build-methods:
    python3 scripts/build_methods.py

# Build data/equivalence/cross_source.tsv — biolink:close_match edges from the
# InterPro member-DB integration (Phase 1 of research/entry-merge-methods-round1).
# Reads docs/data/records.*.json (run `just build-docs` first) + interpro.xml.gz.
build-equivalence:
    python3 scripts/build_equivalence.py

# Build data/equivalence/function.tsv — cross-source biolink:close_match edges
# for FUNCTION records sharing an ontology anchor (EC leaf / RHEA / ARO / TCDB /
# MI), same-category + cross-source only (cross-source-comparison-review-1 §4).
build-function-equivalence:
    python3 scripts/build_function_anchor_equivalence.py

# Build data/equivalence/orthology.tsv — cross-source biolink:close_match edges
# relating OrthoDB / OMA / COG / KOG FUNC_ORTHOLOG_GROUP records that share a
# functional name (relate-only, never merge; issue #20). Generic names capped.
build-orthology-equivalence *args:
    python3 scripts/build_orthology_equivalence.py {{args}}

# Build the residue-frame alignment overlays: seq_struct_alignment.tsv (signature/
# domain/fold edges) + seq_struct_func_sites.tsv (Path 1 — residue-localized
# FUNCTION sites ↔ each other and ↔ the SEQ signatures / STRUCT folds that host
# them). Records sharing an exact canonical-example protein_id whose coordinates
# overlap on the shared UniProt residue frame; relate-only, never a merge
# (research/sequence-structure-function-alignment-analysis-1.md §2 path 1).
#   --providers stored           offline default (pattern hits + own-category FT)
#   --providers stored,interpro,sifts,biolip   full crawl (queries EBI APIs,
#       caches to data/raw/align_cache/; `biolip` maps BioLiP binding residues →
#       UniProt via SIFTS — the ~5.5k STRUCT_BINDING_SITE workhorse)
#   --dry-run for stats; --selftest for offline unit tests.
build-seq-struct-alignment *args:
    python3 scripts/build_sequence_structure_alignment.py {{args}}

# Build data/equivalence/seq_struct_comembership.tsv — Path 2 (whole-protein
# co-membership). SEQUENCE signatures and STRUCT_FOLD records share NO exemplar
# proteins, so the residue-frame path (above) can't connect them. This links a
# signature to the CATH structural-classification record its exemplar proteins are
# consistently classified into (family_classifications CATH id → a STRUCTURE record
# grounded to that CATH). Entity-level `biolink:related_to`, relate-only, never a
# merge. Offline. --min-fraction / --max-cath / --anchor-cap tune the quality gate.
build-seq-struct-comembership *args:
    python3 scripts/build_seq_struct_comembership.py {{args}}

# Build data/equivalence/pathway.tsv — SEED↔Reactome FUNC_PATHWAY equivalence
# from two parallel signals: shared GO biological-process anchor (close_match)
# and constituent EC-set Jaccard (overlaps / close_match). Requires the pathway
# records to be GO-BP / EC grounded first.
build-pathway-equivalence:
    python3 scripts/build_pathway_overlap_equivalence.py

# GO → ChEBI mapping (go-plus logical-definition cross-products) → data/mappings/
# go2chebi.tsv. The .obo/current/snapshot go-plus endpoints 403 to bots; the JSON
# 200s. The tiny TSV is tracked so the docs build needs no 135 MB refetch.
build-go2chebi:
    curl -sSLf -A "Mozilla/5.0" --max-time 300 -o data/raw/go-plus.json https://purl.obolibrary.org/obo/go/extensions/go-plus.json
    python3 scripts/build_go2chebi.py

# Seed the secondary-structure (2°) trait taxonomy — elements / arrangements /
# turns / local + super-secondary motifs — with topology-string representations
# (research/cross-source-comparison-review-1.md). Dry-run by default.
seed-secondary-structure *args:
    python3 scripts/seed_secondary_structure.py {{args}}

# Phase 2 — member-set (Jaccard) overlap between un-integrated signatures.
# Fetches Swiss-Prot member sets from UniProt (cached), blocks on shared
# members, emits data/equivalence/member_overlap.tsv + MERGE candidates.
# Bound a run with --category / --limit; whole-corpus is a long batched job.
build-member-overlap *args:
    python3 scripts/build_member_overlap.py {{args}}

# Phase 3 — structural (Foldseek TM-score) equivalence across CATH/SCOPe/ECOD/
# TED. `--enrich-ted --apply` writes structural_geometry_representations onto TED
# records (no tools); `--derive-ted` builds the representative manifest; the
# default run needs `foldseek` on PATH + AlphaFold model downloads.
build-structural-equivalence *args:
    python3 scripts/build_structural_equivalence.py {{args}}

# Secondary-structure (2°) equivalence — compares STRUCT_SECONDARY entries by
# their topology_string / DSSP-string representation → data/equivalence/
# secondary_structure.tsv. Cross-source by default; --allow-same-source explores.
build-secondary-structure-equivalence *args:
    python3 scripts/build_secondary_structure_equivalence.py {{args}}

# Text-embed every record into a 1024-d vector with a local model (needs the
# `embed` extra: uv sync --extra embed). Reads the docs shards → writes
# data/embeddings/ (gitignored). ~10 min for the full corpus on Apple-Silicon.
embed *args:
    python3 scripts/embed_records.py {{args}}

# Nearest-neighbor "related traits" from the embeddings → docs/data/neighbors.*
# (browser) + Tier-5 semantic merge candidates. Run `just embed` first.
embed-neighbors *args:
    python3 scripts/embed_neighbors.py {{args}}

# UMAP 2-D corpus map + clusters from the embeddings → docs/data/corpus_map.json.
embed-map *args:
    python3 scripts/embed_map.py {{args}}

fetch-repeatsdb:
    mkdir -p data/raw/repeatsdb
    curl -sSLf --max-time 60 -o data/raw/repeatsdb/classification.json https://repeatsdb.org/api/production/classification

seed-repeatsdb *args:
    python3 scripts/seed_repeatsdb.py {{args}}

# Per-structure annotations → classification→member-PDB index (pages the whole
# /api/production/annotations set; ~475 requests). Feeds enrich_repeatsdb_member_reps.
fetch-repeatsdb-annotations:
    python3 scripts/fetch_repeatsdb_annotations.py

# CAZy family classification + resource content (scrapes ~537 per-family cazy.org
# pages: clan, mechanism, fold, activities/EC). © CAZy — academic use, FLAGGED.
fetch-cazy-families:
    python3 scripts/fetch_cazy_families.py

seed-cazy *args:
    python3 scripts/seed_cazy.py {{args}}

fetch-ncbifam:
    mkdir -p data/raw/ncbifam
    curl -sSLf --max-time 120 -o data/raw/ncbifam/hmm_PGAP.tsv https://ftp.ncbi.nlm.nih.gov/hmm/current/hmm_PGAP.tsv

seed-ncbifam *args:
    python3 scripts/seed_ncbifam.py {{args}}

# ORDER MATTERS: the two round-16 builders must run before the round-17 M-CSA
# join, which appends a second graph to records they create. Each builder skips on
# its own graph_id, so a wrong order no longer locks a record out, but it would
# still leave the reaction chemistry missing until re-run.
# Build the Rhea/EC reaction-chemistry graphs and the M-CSA residue join, in order
build-reaction-graphs *args:
    python3 scripts/build_rhea_causal_graphs.py {{args}}
    python3 scripts/build_ec_causal_graphs.py {{args}}
    python3 scripts/build_rhea_mcsa_residue_graphs.py {{args}}

fetch-panther:
    mkdir -p data/raw/panther
    curl -sSLf --max-time 900 -o data/raw/panther/PANTHER19.0_HMM_classifications http://data.pantherdb.org/ftp/hmm_classifications/current_release/PANTHER19.0_HMM_classifications

seed-panther *args:
    python3 scripts/seed_panther.py {{args}}

fetch-cdd:
    mkdir -p data/raw/cdd
    curl -sSLf --max-time 120 -o data/raw/cdd/cddid_all.tbl.gz https://ftp.ncbi.nlm.nih.gov/pub/mmdb/cdd/cddid_all.tbl.gz
    curl -sSLf --max-time 60 -o data/raw/cdd/family_superfamily_links https://ftp.ncbi.nlm.nih.gov/pub/mmdb/cdd/family_superfamily_links

seed-cdd *args:
    python3 scripts/seed_cdd.py {{args}}

fetch-ideal:
    mkdir -p data/raw/ideal
    curl -sSLf --max-time 90 -o data/raw/ideal/IDEAL.xml.gz https://www.ideal-db.org/IDEAL.xml.gz

seed-ideal *args:
    python3 scripts/seed_ideal.py {{args}}

fetch-elm:
    mkdir -p data/raw/elm
    curl -sSLf --max-time 60 -o data/raw/elm/elm_classes.tsv http://elm.eu.org/elms/elms_index.tsv
    curl -sSLf --max-time 90 -o data/raw/elm/elm_instances.tsv "http://elm.eu.org/instances.tsv?q=*"

seed-elm *args:
    python3 scripts/seed_elm.py {{args}}

fetch-merops:
    mkdir -p data/raw/merops
    curl -sSLf --max-time 300 -o data/raw/merops/pepunit.lib https://ftp.ebi.ac.uk/pub/databases/merops/current_release/pepunit.lib
    curl -sSLf --max-time 300 -o data/raw/merops/Substrate_search.txt https://ftp.ebi.ac.uk/pub/databases/merops/current_release/Substrate_search.txt

# Seed protease cleavage-site specificity from MEROPS Substrate_search.txt →
# one SEQ_CLEAVAGE_SITE class per peptidase (P4–P4' consensus). Requires
# `just fetch-merops`. Dry-run by default; --apply / --min-cleavages N.
seed-merops-cleavage *args:
    python3 scripts/seed_merops_cleavage.py {{args}}

seed-merops *args:
    python3 scripts/seed_merops.py {{args}}

# Curated RiPP leader-peptide classes (no fetch)
seed-ripp *args:
    python3 scripts/seed_ripp.py {{args}}

# UniProt peptide feature-type classes (SIGNAL/TRANSIT/PROPEP/… + protein examples)
seed-uniprot-peptides *args:
    python3 scripts/seed_uniprot_peptide_classes.py {{args}}

# ARO (Antibiotic Resistance Ontology, CC-BY) -> FUNC_RESISTANCE (seed-obo aro).
fetch-aro:
    mkdir -p data/raw/aro
    curl -sSLf --max-time 120 -o data/raw/aro/aro.obo https://raw.githubusercontent.com/arpcard/aro/master/src/ontology/aro.obo

# Enrich ARO determinant records with inherited drug-class + mechanism relations
# (CARD confers_resistance_to_drug_class / participates_in, walked up the is_a
# ancestry) as trait_relations — so causal-graph rounds can transcribe the
# resistance shape instead of researching each gene. Idempotent (skips records that
# already have trait_relations); dry-run by default, --apply to write. Needs aro.obo.
enrich-aro-resistance *args:
    python3 scripts/enrich_aro_resistance.py {{args}}

# Auto-DRAFT determinant→mechanism→phenotype causal graphs for ARO records from
# their enriched trait_relations (round-4). Drafts stay SEEDED and carry no verbatim
# snippets (curator adds those before REVIEWED); `audit-graphs --strict` flags them.
# Skips records that already have a hand-curated causal_graphs block. --apply to write.
draft-aro-causal-graphs *args:
    python3 scripts/draft_aro_causal_graphs.py {{args}}

# Curator promotion pass: turn a whole AMR gene family's auto-DRAFT graphs into
# REVIEWED graphs by attaching the family's verbatim literature snippets (one curated
# evidence set promotes every family member). Snippets live in FAMILY_SNIPPETS in the
# script, keyed by family ARO id. --apply to write; --family <ARO:id> required.
# e.g. just promote-family-drafts --family ARO:3000059 --apply   (KPC beta-lactamase)
promote-family-drafts *args:
    python3 scripts/promote_family_drafts.py {{args}}

# Check every family config's claims against the records it would promote (#201).
# Ancestry says the records are RELATED; it does not say the config's MECHANISM is true
# of each one, and three rounds shipped or nearly shipped graphs where it was not --
# every one of them schema-valid, fully grounded and snippet-cited. Two checks: every KB
# CURIE a config grounds a node to must resolve to a record, and each family's optional
# `precondition` must hold for every candidate. Writes nothing; exits non-zero on any
# problem. ~1 minute for all families (the corpus index is built once).
# LOCAL ONLY -- needs data/raw/aro/aro.obo for ancestry, and data/raw is gitignored, so
# this cannot run in CI. Run it before a promotion round, not as a merge gate.
verify-family-drafts *args:
    python3 scripts/promote_family_drafts.py --verify-all {{args}}

# Download the CATH classification names (C/A/T/H hierarchy nodes; CC-BY 4.0).
fetch-cath:
    mkdir -p data/raw/cath
    curl -sSLf --max-time 120 -o data/raw/cath/cath-names.txt ftp://orengoftp.biochem.ucl.ac.uk/cath/releases/latest-release/cath-classification-data/cath-names.txt
    @wc -l data/raw/cath/cath-names.txt

# Seed the CATH structural hierarchy (Class/Architecture/Topology/Homologous
# superfamily). Requires `just fetch-cath`. Dry-run by default; --apply.
seed-cath *args:
    python3 scripts/seed_cath.py {{args}}

# Download the SCOPe parseable files (des + hie; the berkeley host serves
# these fine over https now). Then `just seed-scope --apply`.
fetch-scope-parse:
    mkdir -p data/raw/scope
    curl -sSLf --max-time 120 -o data/raw/scope/dir.des.scope.2.08-stable.txt https://scop.berkeley.edu/downloads/parse/dir.des.scope.2.08-stable.txt
    curl -sSLf --max-time 120 -o data/raw/scope/dir.hie.scope.2.08-stable.txt https://scop.berkeley.edu/downloads/parse/dir.hie.scope.2.08-stable.txt
    # dir.com carries the fold-level structural descriptions (enrich_scop_structural_defs.py)
    curl -sSLf --max-time 120 -o data/raw/scope/dir.com.scope.2.08-stable.txt https://scop.berkeley.edu/downloads/parse/dir.com.scope.2.08-stable.txt
    @ls -la data/raw/scope/

# Download InterPro entries + hierarchy (public domain). Only the small
# entry/abstract/hierarchy files — NOT the multi-TB match files.
fetch-interpro:
    mkdir -p data/raw/interpro
    curl -sSLf --max-time 120 -o data/raw/interpro/entry.list \
      https://ftp.ebi.ac.uk/pub/databases/interpro/current_release/entry.list
    curl -sSLf --max-time 120 -o data/raw/interpro/ParentChildTreeFile.txt \
      https://ftp.ebi.ac.uk/pub/databases/interpro/current_release/ParentChildTreeFile.txt
    curl -sSLf --max-time 600 -o data/raw/interpro/interpro.xml.gz \
      https://ftp.ebi.ac.uk/pub/databases/interpro/current_release/interpro.xml.gz
    @ls -la data/raw/interpro/

# Fetch InterPro member-database signature lists (PIRSF/PRINTS/SSF/SFLD/SMART/HAMAP)
# from the EBI API. The FTP has no per-member-DB file, and SUPERFAMILY has no name
# at all in interpro.xml.gz -- see the script docstring. Dry-run by default.
fetch-interpro-members *args:
    uv run python scripts/fetch_interpro_members.py {{args}}

# Seed data/traits/ from an InterPro member database. Requires
# `just fetch-interpro` and `just fetch-interpro-members --db <db> --apply`.
# Dry-run by default; --apply to write.
seed-interpro-members *args:
    python3 scripts/seed_interpro_members.py {{args}}

# Seed data/traits/ from InterPro entries (Domain, Homologous_superfamily,
# Repeat, Conserved_site, Active/Binding_site, PTM; Family excluded by
# default). Requires `just fetch-interpro`. Dry-run by default; --apply.
seed-interpro *args:
    python3 scripts/seed_interpro.py {{args}}

# Download the current PSI-MOD OBO release (HUPO-PSI/psi-mod-CV, CC-BY-4.0).
fetch-psimod:
    mkdir -p data/raw
    curl -sSLf --max-time 120 -o data/raw/PSI-MOD.obo \
      https://raw.githubusercontent.com/HUPO-PSI/psi-mod-CV/master/PSI-MOD.obo
    @ls -la data/raw/PSI-MOD.obo

# Seed data/traits/sequence/{modified_residue,glycosylation,lipidation,
# crosslink,ptm_ontology}/ from PSI-MOD. Requires `just fetch-psimod`.
# Dry-run by default; --apply to write. Idempotent.
seed-psimod *args:
    python3 scripts/seed_psi_mod.py {{args}}

# Download the OBO ontologies consumed by seed-obo (PSI-MI, PATO, METPO;
# all CC-BY-4.0). Files land gitignored in data/raw/.
fetch-obo:
    mkdir -p data/raw
    curl -sSLf --max-time 120 -o data/raw/PSI-MI.obo \
      https://raw.githubusercontent.com/HUPO-PSI/psi-mi-CV/master/psi-mi.obo
    curl -sSLf --max-time 120 -o data/raw/PATO.obo \
      https://raw.githubusercontent.com/pato-ontology/pato/master/pato.obo
    curl -sSLf --max-time 120 -o data/raw/METPO.obo \
      https://raw.githubusercontent.com/berkeleybop/metpo/main/metpo.obo
    curl -sSLf --max-time 300 -o data/raw/go-basic.obo \
      http://purl.obolibrary.org/obo/go/go-basic.obo
    @ls -la data/raw/PSI-MI.obo data/raw/PATO.obo data/raw/METPO.obo data/raw/go-basic.obo

# Seed ProteinTraitRecords from branch-scoped OBO ontologies. Requires
# `just fetch-obo`. Pass a source (psimi | pato | metpo | all). Dry-run
# by default; --apply to write. Idempotent.
#   just seed-obo psimi
#   just seed-obo all --apply
seed-obo *args:
    python3 scripts/seed_obo.py {{args}}

# Download Pfam-A + mappings (public domain). Pfam-B is discontinued (Pfam 28).
fetch-pfam:
    mkdir -p data/raw/pfam data/raw/mappings
    curl -sSLf --max-time 300 -o data/raw/pfam/Pfam-A.clans.tsv.gz https://ftp.ebi.ac.uk/pub/databases/Pfam/current_release/Pfam-A.clans.tsv.gz
    curl -sSLf --max-time 300 -o data/raw/pfam/Pfam-A.hmm.dat.gz  https://ftp.ebi.ac.uk/pub/databases/Pfam/current_release/Pfam-A.hmm.dat.gz
    gzcat data/raw/pfam/Pfam-A.hmm.dat.gz | awk '/^#=GF AC/{ac=$3; sub(/\\..*/,"",ac)} /^#=GF TP/{print ac"\\t"$3}' > data/raw/pfam/pfam_types.tsv
    curl -sSLf --max-time 120 -o data/raw/mappings/pfam2go https://current.geneontology.org/ontology/external2go/pfam2go
    @echo 'pfam2interpro.tsv is derived from data/raw/interpro/interpro.xml.gz (run fetch-interpro)'
    @echo 'NOTE (#344): that TSV is AMBIGUOUS — it mixes "PF is a member signature of IPR"'
    @echo '  with "IPR abstract mentions PF", and 467 accessions carry both. Nothing reads'
    @echo '  it for that question any more; seed-pfam, enrich_pfam_definitions and'
    @echo '  migrate_mapped_xrefs all take member_list straight from interpro.xml.gz.'

# Seed Pfam-A families (Domain/Family/Repeat/Coiled-coil/Disordered/Motif),
# GO- + InterPro-grounded. Requires `just fetch-pfam`. Dry-run by default.
seed-pfam *args:
    python3 scripts/seed_pfam.py {{args}}

# Copy the ENIGMA trait-onto-map catalogue into data/raw/ (gitignored). The
# source is a local sibling repo — adjust the path for your machine.
fetch-traitontomap:
    mkdir -p data/raw/traitontomap
    cp /Users/marcin/Documents/VIMSS/ontology/ENIGMA/trait-onto-map/data/catalog/trait_catalog.tsv data/raw/traitontomap/
    @ls -la data/raw/traitontomap/

# Seed data/traits/function/enzymatic_activity/traitontomap/ from the ENIGMA
# trait-onto-map catalogue — EC-grounded enzyme activities only. Requires
# `just fetch-traitontomap`. Dry-run by default; --apply.
seed-traitontomap *args:
    python3 scripts/seed_traitontomap.py {{args}}

# Seed data/traits/evolution/ with evolutionary / pangenome traits
# (conserved, clade-specific, variable; pangenome core/soft-core/shell/
# cloud/persistent/singleton). Curator-minted. Dry-run by default; --apply.
seed-evolution *args:
    python3 scripts/seed_evolution.py {{args}}

# Seed data/traits/structure/stability/conditions/ with condition-specific
# structural-stability traits (thermal/oxidative/saline/pH/osmotic/pressure/
# desiccation/chemical/proteolytic/mechanical × increased/decreased). Curator-
# minted, parented to the PATO stability terms. Dry-run by default; --apply.
seed-stability *args:
    python3 scripts/seed_stability.py {{args}}

# Seed data/traits/ from UniProtKB FT lines. Accepts flags:
#   --accession <ACC>     fetch from UniProt REST (repeat for many)
#   --from-file <path>    one accession per line
#   --input <path>        local flat file (may hold many entries)
# Dry-run by default; --apply to write. Idempotent.
seed-uniprot *args:
    python3 scripts/seed_uniprot.py {{args}}

# Ground `trait_category` values to authoritative ontology terms (SO,
# GO, MOD) via a curated mapping. Uses OAK's sqlite:obo adapter by
# default (--source oak) or the OLS4 REST API (--source ols) to verify
# each CURIE. --audit prints the resolved table; --apply adds the
# resolved CURIEs to each record's xrefs (idempotent).
#   just ground-categories --audit
#   just ground-categories --apply
ground-categories *args:
    uv run python scripts/ground_categories.py {{args}}

# Populate canonical_examples on trait YAMLs by querying the UniProtKB
# REST API for entries carrying each trait's anchoring signature
# (PROSITE / Pfam / InterPro / HAMAP / etc.). Dry-run by default; pass
# --apply to write. Rate-limited (~4 req/s) with backoff.
#   just fetch-examples data/traits/sequence/pattern/1433-1.yaml --limit 5 --apply
#   just fetch-examples data/traits/sequence/motif --limit 3 --apply
fetch-examples *args:
    uv run python scripts/fetch_uniprot_examples.py {{args}}

# Build per-protein trait PROFILES from Swiss-Prot (issue #7): for each entry,
# which corpus trait classes it carries (matched via Pfam/InterPro/CATH/PROSITE/
# SMART/CDD/NCBIfam/EC/GO) + its GO/EC — the protein×trait matrix for trait↔GO
# correlation + multi-trait-family clustering. --query / --limit bound the slice;
# --apply writes data/profiles/<acc>.yaml (ProteinProfile) + profiles.jsonl.
#   just build-profiles --query "reviewed:true AND organism_id:9606" --limit 1000 --apply
# --query repeats for a multi-organism matrix; --organisms is shorthand for the
# standard four (human / mouse / yeast / E. coli K-12) and --limit caps per query.
#   just build-profiles --organisms --limit 25000 --jsonl-only --apply
build-profiles *args:
    python3 scripts/build_swissprot_profiles.py {{args}}

# Held-out-organism replication test for the phase-3/4 cross-axis rules (issue #7,
# phase 6): mine on one organism, recompute each rule's confidence on the others.
# Answers "are these rules biology or an artefact of the human proteome?".
# Needs a multi-organism matrix (see build-profiles --organisms). Stdlib-only.
#   just test-rule-generalization --train 9606
test-rule-generalization *args:
    python3 scripts/test_rule_generalization.py {{args}}

# 2-D map of the protein×trait matrix → docs/data/protein_map.json (issue #7,
# phase 8), rendered by the "Proteins" tab on docs/map.html. One point per
# Swiss-Prot protein, positioned by the corpus traits it carries, coloured by
# organism and filterable by CATH class. Needs numpy/scipy/scikit-learn/pacmap —
# run with system python3 (as here), not uv.
#   just protein-map --sample 20000
protein-map *args:
    python3 scripts/build_protein_map.py {{args}}

# Multi-trait families (issue #7): DiviK-style divisive clustering of the
# protein×trait matrix — top-down splits with local feature re-selection at each
# node, per doi:10.1186/s12859-022-05093-z. Emits data/families/trait_families.tsv
# with each family's core traits. Clusters with no shared core are reported as
# unassigned rather than called families. Needs numpy/scipy/scikit-learn.
#   just cluster-families --max-depth 40 --min-silhouette 0.02 --apply
cluster-families *args:
    python3 scripts/cluster_trait_families.py {{args}}

# Test what a corpus map actually organises by (issue #7, phase 9). The browser
# colours by trait axis; this measures neighbour purity for axis vs SOURCE
# DATABASE, in the embedding and in the 2-D map, plus a full-corpus retrieval
# counter-test on known cross-source equivalent pairs. Read-only.
# Also reports 2-D layout degeneracy, which purity cannot see — use --layout-only
# for maps with no text embedding (protein_map.json), which needs no --emb-dir.
#   just measure-map --map corpus_map_definitions.json --emb-dir data/embeddings/definition
#   just measure-map --map protein_map.json --layout-only
measure-map *args:
    python3 scripts/measure_map_structure.py {{args}}

# Residue-frame sidecar for the exemplar proteins (issue #7, phase 10): UniProt
# sequence + FT intervals routed to trait categories, keyed by accession, so the
# Path 1 aligner can localize records on their SWISSPROT_PROFILE exemplars
# without inlining a sequence into every record. Gitignored + regenerable.
#   just fetch-residue-frame --organisms --apply
# All three align_cache sidecars carry a provenance header (issue #57): source
# database + release + build date. The fetchers refuse to resume across a release
# change unless --allow-stale, because resuming would mix coordinates from two
# releases into one overlay and nothing downstream could tell.
fetch-residue-frame *args:
    python3 scripts/fetch_residue_frame.py {{args}}

# InterPro match sidecar (issue #7, phase 11): every member-DB signature match
# with coordinates, per protein, for the exemplar proteins that could actually
# yield a residue-frame edge. Localizes domain/family records, which the residue
# frame cannot (a UniProt DOMAIN interval says "a domain is here", not which
# signature). Crawls per protein, not per (signature, protein) — 15,120 calls
# instead of 63,718. Resumable + checkpointed; gitignored.
#   just fetch-interpro-frame --apply
fetch-interpro-frame *args:
    python3 scripts/fetch_interpro_frame.py {{args}}

# Adjudicate the identical-residue-set links from the alignment overlay (issue #7,
# phase 12): a CATH superfamily and an InterPro entry covering the same residues
# are the same superfamily under two identifiers only if InterPro actually
# integrates that Gene3D signature. Confirmed pairs become a biolink:close_match
# overlay (data/equivalence/residue_identity.tsv); the rest stay related_to.
#   just verify-residue-identity --apply
verify-residue-identity *args:
    python3 scripts/verify_residue_identity.py {{args}}

# Train interpretable trait->GO-function decision trees on the protein×trait matrix
# (data/profiles/profiles.jsonl). "Predict function from the presence of certain
# traits" (issue #7). Needs scikit-learn — run with system python3 (as here), not uv.
train-trait-tree *args:
    python3 scripts/train_trait_go_tree.py {{args}}

# Cross-axis trait correlations (issue #7): does a sequence signature always encode a
# structural fold? which traits imply which GO/EC function? Association rules
# (confidence + lift) over data/profiles/profiles.jsonl. Stdlib-only.
# Function edges are split by GO aspect (molecular-function / biological-process /
# localization / enzymatic-activity) because phase 6 showed they do not deserve
# equal trust. Each edge also carries an organism-balanced confidence and the
# number of proteomes that voted; --min-balanced-conf gates on it (default off).
trait-correlations *args:
    python3 scripts/analyze_trait_correlations.py {{args}}

# Write canonical_examples onto trait records from the protein×trait matrix
# (issue #7, phase 5) — closes the loop from mined cross-axis rules back to real
# proteins. Carriers are ranked by how many of the trait's empirically coupled
# partners (data/equivalence/trait_cooccurrence.tsv) they also carry. Records
# that already have examples are skipped. Dry-run unless --apply. Needs PyYAML.
#   just suggest-examples --prefix CATH --apply
#   just suggest-examples --rule-backed-only --apply
suggest-examples *args:
    uv run python scripts/suggest_canonical_examples.py {{args}}

# Regenerate docs/data/records.json + facets.json used by the browse
# page. Requires PyYAML; walks every data/traits/**/*.yaml.
build-docs:
    python3 scripts/build_docs_index.py

# Compose all layered definitions (GENERAL / STRUCTURAL / MECHANISTIC) across the
# corpus, idempotently, in dependency order: base source layers first, then the
# self-contained composers, then the cross-record inheritance passes (which read
# the base layers). Re-run after any (re-)seed to restore the layers a seeder's
# raw import doesn't carry. Dry-run by default; pass --apply to write.
#   just enrich-definitions            # dry-run (all composers report counts)
#   just enrich-definitions --apply    # write
enrich-definitions *args:
    # Phase 1 — base source layers (inheritance below reads these).
    python3 scripts/enrich_ec_general_defs.py {{args}}
    python3 scripts/enrich_mechanistic_defs.py {{args}}
    python3 scripts/enrich_scop_structural_defs.py {{args}}
    python3 scripts/enrich_scop_inherited_structural.py {{args}}
    python3 scripts/enrich_cath_structural_defs.py {{args}}
    python3 scripts/enrich_ecod_structural_defs.py {{args}}
    python3 scripts/enrich_structural_provenance.py {{args}}
    # Phase 2 — self-contained composers (a record's own content).
    python3 scripts/enrich_go_mf_mechanistic_defs.py {{args}}
    python3 scripts/enrich_interaction_mechanistic_defs.py {{args}}
    python3 scripts/enrich_secondary_structural_defs.py {{args}}
    # Phase 3 — cross-record inheritance (must follow Phase 1).
    python3 scripts/enrich_seq_structural_inherited_defs.py {{args}}
    python3 scripts/enrich_family_mechanistic_inherited_defs.py {{args}}

# Analyze the catalog for equivalent, mergeable traits. Emits unequivocal
# "Trait X = Trait Y" statements (deterministic) plus a separate review
# list. Reads docs/data shards, so run `just build-docs` first. Dry-run by
# default; --apply executes the MERGE groups (never the review candidates).
#   just analyze-merges                 # dry-run + write plan
#   just analyze-merges --show-review   # also list review candidates
#   just analyze-merges --apply         # execute merges
analyze-merges *args:
    python3 scripts/analyze_trait_equivalence.py {{args}}

# Shortlist records whose own definition names a role their curated graph contradicts
audit-roles:
    uv run python scripts/audit_role_mismatch.py

# Fetch the abstracts interpro.xml.gz omits but the InterPro API has (#445).
# 209 of the release's 54,190 entries ship no <abstract>; every one of them has a
# curator-written description in the API, 811-5,326 chars. That gap left 45 Pfam records
# and 60 InterPro records defining themselves by their own name.
# NETWORK, and CACHED. ~209 calls at 0.35s apart, ~2 minutes cold, seconds warm. Writes
# data/raw/ (gitignored) like every other source here: nothing fetched is committed, the
# corpus is rebuilt from sources rather than from checked-in copies of them, and that holds
# for 209 REST calls exactly as for a release tarball. `api_cache.json` is what makes the
# second kind as cheap to re-materialise as the first, and is safe to delete.
# Transient failures are never cached, so a flaky minute cannot become a permanent
# "absent"; a run that fails refuses to overwrite a good artefact, and the retry fetches
# only the gap.
# Canary it: `--limit 1` fetches one, prints the provenance flags, and refuses to write.
fetch-interpro-missing-abstracts *args:
    uv run python scripts/fetch_interpro_missing_abstracts.py {{args}}

# Promote those descriptions onto the records that have no definition without them (#445).
# Two scripts because two owners: enrich_pfam_definitions owns Pfam definitions and would
# fight a second writer for the same field, so the Pfam half lives inside it.
# Neither promotes an LLM-generated description (#92) or touches a curated record (#175).
# Both dry-run by default.
enrich-missing-abstracts *args:
    uv run python scripts/enrich_pfam_definitions.py {{args}}
    uv run python scripts/enrich_interpro_missing_abstracts.py {{args}}

# Do the records agree with the equivalence overlay they were built from? (#447)
# cross_source.tsv and a record's mapped_xrefs say the same thing in two places, both
# derived from interpro.xml's member_list, and nothing compared them -- so the committed
# TSV held the right Pfam->InterPro pairs while 335 records asserted a different entry,
# for the whole life of #344.
# Reads ONLY committed files, so unlike audit-pfam-interpro it CAN run in CI (data/raw is
# gitignored). It does so via pytest, not this recipe: checks.yml runs `just lint` and
# `just test`, and tests/test_equivalence_consistency.py shells out to the script. This
# recipe is for running it by hand.
# It is the cheap gate: a CONSISTENCY check, not a correctness one -- if both artefacts
# were regenerated from the same bad parse it would pass. Run both locally.
# It compares 17,970 of the 29,105 pairs it COULD compare and prints what it did not,
# in both directions -- including 6,329 overlay rows no record asserts, which nothing
# covers (#450).
audit-equivalence-consistency *args:
    uv run python scripts/audit_equivalence_consistency.py {{args}}

# Does each Pfam record cite the InterPro entry that INTEGRATES it? (#344)
# `pfam2interpro.tsv` mixes "PF is a member of IPR" with "IPR's abstract mentions PF", and
# the readers took the last row -- so 407 records carried a neighbouring domain's abstract
# as their definition. Fluent, on-topic, self-consistent and about something else, which is
# why validate-all, audit-prose and every link check passed it.
# No baseline and no ceiling: unlike #425's archetypes there are no legitimate instances.
# LOCAL ONLY -- needs data/raw/interpro/interpro.xml.gz; without it this FAILS rather than
# reporting 0 against a reference it does not have (#432's lesson).
audit-pfam-interpro *args:
    uv run python scripts/audit_pfam_interpro.py {{args}}

# Repair what audit-pfam-interpro finds (#344). Definitions FIRST: the xref repair reads
# the same member_list and the two must agree, and running them the other way round leaves
# a record whose definition and xref name different entries until the second finishes.
# Both are dry-run by default.
repair-pfam-interpro *args:
    uv run python scripts/enrich_pfam_definitions.py {{args}}
    uv run python scripts/repair_pfam_interpro_xrefs.py {{args}}

# Does each promoter-owned record still match what its config would emit today? (#408)
# `--verify-all` checks that a config's CURIEs RESOLVE; nothing checked that the records it
# OWNS match what it would write, so config edits landed without --repromote and the corpus
# drifted silently -- 443 of 1,142 at filing.
# BUCKETS, not a count, and that is the point: 449 records once differed by TEXT while only
# 78 differed once parsed. A scalar mixes pure YAML layout with real semantic drift, so
# re-promoting 371 no-ops would have read as progress.
# `structure` is the bucket that matters -- mdfA and tet(M) are there because a curator
# added literature the config lacks, so re-promoting them would DESTROY it (#204). This
# reports; it never repairs.
# Pinned at 31 with an identity baseline, because a ceiling masks a swap (#411).
# LOCAL ONLY -- needs data/raw/aro/aro.obo; without it this FAILS rather than reporting 0
# drift over 0 records (#432).
audit-reproducible *args:
    uv run python scripts/audit_reproducible.py \
        --max-drift 5074 --baseline audit/reproducible-baseline.json {{args}}

# Rewrite the notes that call a record its own is_a ancestor (#364).
# `_drug_assertion` walks is_a from the record UPWARD with the record itself first, and
# used one wording for both branches -- so every direct assertion claimed the record was
# its own ancestor. The promoter is fixed; this repaired the 215 notes already on disk.
# The count took three corrections to settle: a raw-text regex, a greedy one, and a
# substring prefilter each hid a different slice of it (#462).
# Not `fix_resistance_drug_edges`: that owns the same wording but selects only
# `resistance -> drug*` edges, and these sit on `determinant -> drug0`.
# Dry-run by default.
repair-self-referential-notes *args:
    uv run python scripts/repair_self_referential_notes.py {{args}}

# Which already-curated records would no config accept today (#267)
# LOCAL ONLY -- reads data/raw/aro/aro.obo, which is gitignored; run `just fetch-aro`
# first. Exits 1 if it examined nothing, so a 0 here means 0 (#469).
audit-fit:
    uv run python scripts/audit_config_fit.py

# Which drafts would a config accept, and which does a configured family refuse (#316)
audit-drafts:
    uv run python scripts/audit_refused_drafts.py

# Does every cited snippet actually appear in the source it names? (#365)
# TWO gates. --max pins the COUNT (0; was 287, then 174 after the repoints, then 41 after
# #423's truncation repair, then 0 once #422 resolved the last two misattributions).
# --baseline pins the IDENTITY of each known mismatch, because a ceiling masks a SWAP:
# fixing one while introducing another leaves the total unchanged and a count gate green
# (#411, demonstrated). Both baselines are now EMPTY, which makes the ceiling and the
# identity gate agree: any mismatch at all is new, and fails.
# After fixing some, re-run with --update-baseline to lock the progress in.
# --configs checks the FAMILY_SNIPPETS literals too: nothing did, which is how #423
# shipped two corrupt snippets past every other gate (#424). It gets BOTH gates for
# the same reason the data side does -- a ceiling masks a swap (#411, #428).
#
# --archetypes is a THIRD, different question (#425): the snippet is verbatim in the term
# it cites and still wrong for the record, because that term is one gene in one organism
# and this record is neither. No quote-checker can see that, which is why carO's
# definition sat on 42 records -- 2 of them carO -- until #423 restored the clause naming
# Acinetobacter baumannii and made it visible.
# Pinned at 323 (was 414 before carO and the basR/basS role split), NOT at 0: unlike the
# other two, a hit here is not automatically a defect. An efflux repressor citing the pump
# it represses is citing the edge's own object. The 323 are a REVIEW QUEUE, triaged in the
# issue this pin was set from; the gate's job is that the queue cannot silently grow.
#
# LOCAL ONLY -- needs `data/raw/aro/aro.obo`, and data/raw is gitignored, so without it
# every ARO reference is unverifiable and this reports 0 mismatches against 29,590 items it
# never compared. It says so loudly; pass --require-aro to make that a failure instead of a
# note. The pytest regression SKIPS when the obo is absent rather than passing a ceiling on
# nothing, and --archetypes turns ITSELF off rather than reporting an empty queue as
# progress (#432).
audit-snippets *args:
    uv run python scripts/audit_snippets.py --path function/resistance/aro \
        --max 0 --baseline audit/snippet-mismatch-baseline.json \
        --configs --max-configs 0 \
        --config-baseline audit/config-literal-baseline.json \
        --archetypes --max-archetypes 323 \
        --archetype-baseline audit/archetype-baseline.json {{args}}
