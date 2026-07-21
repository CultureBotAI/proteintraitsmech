# ProteinTraitsMech - protein sequence & structure trait knowledge base

set dotenv-load := true

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

# Validate the data-source registry (data/sources.yaml) and cross-check it
# against the seeders. Warns on restrictive (NC/ND) licences + orphan seeders.
sources-check:
    python3 scripts/check_sources.py

# Structural-integrity audit of causal graphs
audit-graphs *args:
    uv run python scripts/audit_causal_graphs.py {{args}}

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
