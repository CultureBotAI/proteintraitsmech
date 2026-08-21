from __future__ import annotations

import importlib.util
import pathlib
import sys

import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "check_sources.py"


def _load():
    spec = importlib.util.spec_from_file_location("check_sources", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


CHECK = _load()


def _run(tmp_path, blocks, helpers=(), scripts=()):
    manifest = tmp_path / "download.yaml"
    helper_path = tmp_path / "source_helpers.yaml"
    script_dir = tmp_path / "scripts"
    script_dir.mkdir(exist_ok=True)
    manifest.write_text(yaml.safe_dump(blocks, sort_keys=False), encoding="utf-8")
    helper_path.write_text(yaml.safe_dump(list(helpers), sort_keys=False), encoding="utf-8")
    for name in scripts:
        (script_dir / name).write_text("", encoding="utf-8")
    return CHECK.validate_registry(manifest, helper_path, script_dir)


def test_later_block_cannot_hide_an_earlier_seeded_source_without_a_seeder(tmp_path):
    result = _run(
        tmp_path,
        [
            {"url": "https://example.org/data", "source": "same", "status": "seeded"},
            {"url": "https://example.org/map", "source": "same", "status": "deferred"},
        ],
    )
    assert any("seeded block but no block names a seeder" in error for error in result.errors)


def test_per_accession_api_names_a_fetcher_not_a_seeder(tmp_path):
    result = _run(
        tmp_path,
        [
            {
                "url": "https://example.org/api/{accession}",
                "source": "api",
                "status": "enrichment",
                "role": "api",
                "fetcher": "fetch_api.py",
            }
        ],
        scripts=["fetch_api.py"],
    )
    assert result.errors == []


def test_a_fetcher_filed_as_a_seeder_fails(tmp_path):
    result = _run(
        tmp_path,
        [
            {
                "url": "https://example.org/api",
                "source": "bad",
                "status": "seeded",
                "seeder": "fetch_api.py",
            }
        ],
        scripts=["fetch_api.py"],
    )
    assert any("seeder must name a seed_*.py" in error for error in result.errors)


def test_enrichment_and_local_generator_roles_are_explicit(tmp_path):
    result = _run(
        tmp_path,
        [
            {
                "url": "https://example.org/data",
                "source": "chemistry",
                "status": "enrichment",
                "role": "enrichment",
                "enricher": "build_sidecar.py",
            }
        ],
        helpers=[
            {
                "script": "seed_local_taxonomy.py",
                "role": "local_generator",
                "reason": "Project-authored bounded vocabulary.",
            }
        ],
        scripts=["build_sidecar.py", "seed_local_taxonomy.py"],
    )
    assert result.errors == []


def test_an_unclassified_seeder_is_an_error(tmp_path):
    result = _run(tmp_path, [], scripts=["seed_orphan.py"])
    assert any("seed_orphan.py is unclassified" in error for error in result.errors)


def test_unknown_status_role_and_missing_scripts_fail(tmp_path):
    result = _run(
        tmp_path,
        [
            {
                "url": "https://example.org/data",
                "source": "broken",
                "status": "mystery",
                "role": "mystery",
                "seeder": "seed_missing.py",
            }
        ],
    )
    joined = "\n".join(result.errors)
    assert "invalid status" in joined
    assert "invalid role" in joined
    assert "script not found" in joined


def test_restrictive_terms_require_an_explicit_review_state(tmp_path):
    block = {
        "url": "https://example.org/data",
        "source": "restricted",
        "status": "candidate",
        "license": "NonCommercial — FLAGGED",
    }
    result = _run(tmp_path, [block])
    assert any("must declare license_review" in error for error in result.errors)

    block["license_review"] = "pending"
    reviewed = _run(tmp_path, [block])
    assert reviewed.errors == []
    assert reviewed.notices == [
        "[restricted] licence disposition pending under #517"
    ]
