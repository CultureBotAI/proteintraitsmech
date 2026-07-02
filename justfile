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
    curl -sS --fail --max-time  30 -o data/raw/ps_reldt.txt ftp://ftp.expasy.org/databases/prosite/ps_reldt.txt
    @cat data/raw/ps_reldt.txt

# Seed data/traits/ from PROSITE patterns / profiles / ProRules.
# Requires `just fetch-prosite` first. Dry-run by default; --apply to write.
seed-prosite *args:
    python3 scripts/seed_prosite.py {{args}}

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
    @ls -la data/raw/PSI-MI.obo data/raw/PATO.obo data/raw/METPO.obo

# Seed ProteinTraitRecords from branch-scoped OBO ontologies. Requires
# `just fetch-obo`. Pass a source (psimi | pato | metpo | all). Dry-run
# by default; --apply to write. Idempotent.
#   just seed-obo psimi
#   just seed-obo all --apply
seed-obo *args:
    python3 scripts/seed_obo.py {{args}}

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

# Analyze the catalog for equivalent, mergeable traits. Emits unequivocal
# "Trait X = Trait Y" statements (deterministic) plus a separate review
# list. Reads docs/data shards, so run `just build-docs` first. Dry-run by
# default; --apply executes the MERGE groups (never the review candidates).
#   just analyze-merges                 # dry-run + write plan
#   just analyze-merges --show-review   # also list review candidates
#   just analyze-merges --apply         # execute merges
analyze-merges *args:
    python3 scripts/analyze_trait_equivalence.py {{args}}
