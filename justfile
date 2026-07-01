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

# Validate every YAML under data/traits/
validate-all *args:
    @just validate-strict {{args}}

# Strict in-process closed-mode validation
validate-strict *args:
    uv run python scripts/validate_strict.py {{args}}

# Programmatic schema-quality probes
audit-schema:
    uv run python scripts/audit_schema.py

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
