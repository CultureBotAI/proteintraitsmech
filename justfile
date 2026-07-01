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
