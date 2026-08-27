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
    assert reviewed.notices == ["[restricted] licence disposition pending under #517"]


# ---------------------------------------------------------------------------------------
# Every rule below could be deleted with the suite staying green (#543). The tests that
# existed defended the four rules they were written for and none of the rules #528 newly
# wrote, so each of these names one rule and asserts the message it produces.
# ---------------------------------------------------------------------------------------

OK_BLOCK = {"url": "https://example.org/x", "source": "s", "status": "candidate"}


def _errors(tmp_path, blocks, helpers=(), scripts=()):
    return _run(tmp_path, blocks, helpers, scripts).errors


def test_url_is_required(tmp_path):
    assert any(
        "missing required field: url" in e
        for e in _errors(tmp_path, [{"source": "s", "status": "candidate"}])
    )


def test_fetcher_must_be_named_fetch(tmp_path):
    blocks = [dict(OK_BLOCK, fetcher="seed_wrong.py")]
    assert any(
        "fetcher must name a fetch_*.py script" in e
        for e in _errors(tmp_path, blocks, scripts=["seed_wrong.py"])
    )


def test_enricher_must_not_be_named_like_a_seeder_or_fetcher(tmp_path):
    blocks = [dict(OK_BLOCK, enricher="fetch_thing.py")]
    assert any(
        "enricher must not be named like a seeder or fetcher" in e
        for e in _errors(tmp_path, blocks, scripts=["fetch_thing.py"])
    )


def test_license_review_value_must_be_known(tmp_path):
    blocks = [dict(OK_BLOCK, license="NonCommercial", license_review="probably-fine")]
    assert any("invalid license_review" in e for e in _errors(tmp_path, blocks))


def test_restrictive_licence_must_declare_a_review(tmp_path):
    blocks = [dict(OK_BLOCK, license="CC BY-NC-ND 4.0")]
    assert any("must declare license_review" in e for e in _errors(tmp_path, blocks))


def test_approved_restrictive_licence_must_name_who_approved_it(tmp_path):
    """`approved` produced zero errors and zero notices, so a restrictive licence could
    be waved through leaving no approver, date or issue behind (#543)."""
    blocks = [dict(OK_BLOCK, license="NonCommercial", license_review="approved")]
    assert any("must carry license_review_ref" in e for e in _errors(tmp_path, blocks))

    result = _run(
        tmp_path,
        [
            dict(
                OK_BLOCK,
                license="NonCommercial",
                license_review="approved",
                license_review_ref="#517 (owner)",
            )
        ],
    )
    assert result.errors == []
    assert any("restrictive licence approved" in n for n in result.notices)


def test_a_block_with_no_licence_is_reported(tmp_path):
    result = _run(tmp_path, [OK_BLOCK])
    assert any("no licence recorded" in n for n in result.notices)


def test_status_without_source_is_rejected(tmp_path):
    """Grouping is by `source:`, so such a block was checked for url and nothing else,
    including the seeded-needs-a-seeder rule (#543)."""
    blocks = [{"url": "https://example.org/x", "status": "seeded"}]
    assert any("joins no source group" in e for e in _errors(tmp_path, blocks))


def test_an_api_block_may_not_be_seeded(tmp_path):
    """Nothing linked role to status, so a per-accession API could call itself seeded
    while a sibling supplied the seeder -- the shape of #458 (#543)."""
    blocks = [
        dict(OK_BLOCK, role="api", status="seeded"),
        dict(OK_BLOCK, seeder="seed_s.py", status="seeded"),
    ]
    assert any(
        "role: api may not be status: seeded" in e
        for e in _errors(tmp_path, blocks, scripts=["seed_s.py"])
    )


def test_a_helper_classified_twice_is_rejected(tmp_path):
    helpers = [
        {"script": "seed_h.py", "role": "helper_seeder", "reason": "r"},
        {"script": "seed_h.py", "role": "helper_seeder", "reason": "r"},
    ]
    assert any(
        "classified more than once" in e
        for e in _errors(tmp_path, [OK_BLOCK], helpers, ["seed_h.py"])
    )


def test_a_seeder_cannot_be_both_source_backed_and_helper_classified(tmp_path):
    blocks = [dict(OK_BLOCK, seeder="seed_h.py", status="seeded")]
    helpers = [{"script": "seed_h.py", "role": "helper_seeder", "reason": "r"}]
    assert any(
        "both source-backed and helper-classified" in e
        for e in _errors(tmp_path, blocks, helpers, ["seed_h.py"])
    )


def test_a_helper_entry_requires_a_reason(tmp_path):
    helpers = [{"script": "seed_h.py", "role": "helper_seeder"}]
    assert any(
        "requires a reason" in e for e in _errors(tmp_path, [OK_BLOCK], helpers, ["seed_h.py"])
    )


def test_a_helper_role_must_be_known(tmp_path):
    helpers = [{"script": "seed_h.py", "role": "assistant", "reason": "r"}]
    assert any(
        "invalid helper role" in e for e in _errors(tmp_path, [OK_BLOCK], helpers, ["seed_h.py"])
    )


def test_the_helper_registry_only_classifies_seeders(tmp_path):
    helpers = [{"script": "fetch_h.py", "role": "helper_seeder", "reason": "r"}]
    assert any(
        "may only classify seed_*.py scripts" in e
        for e in _errors(tmp_path, [OK_BLOCK], helpers, ["fetch_h.py"])
    )


def test_a_helper_script_must_exist(tmp_path):
    helpers = [{"script": "seed_absent.py", "role": "helper_seeder", "reason": "r"}]
    assert any("helper script not found" in e for e in _errors(tmp_path, [OK_BLOCK], helpers))


def test_a_block_that_is_not_a_mapping_is_rejected(tmp_path):
    assert any("must be a mapping" in e for e in _errors(tmp_path, ["just a string"]))


def test_a_script_field_must_be_a_non_empty_command_string(tmp_path):
    assert any(
        "must be a non-empty command string" in e
        for e in _errors(tmp_path, [dict(OK_BLOCK, seeder=17)])
    )


def test_a_manifest_that_is_not_a_list_is_rejected(tmp_path):
    manifest = tmp_path / "download.yaml"
    helper_path = tmp_path / "source_helpers.yaml"
    script_dir = tmp_path / "scripts"
    script_dir.mkdir(exist_ok=True)
    manifest.write_text("not: a list\n", encoding="utf-8")
    helper_path.write_text("[]\n", encoding="utf-8")
    result = CHECK.validate_registry(manifest, helper_path, script_dir)
    assert any("must be a YAML list" in e for e in result.errors)


def test_an_unregistered_fetch_script_is_reported(tmp_path):
    """Orphan detection globbed seed_*.py only, so a fetch route was invisible (#543)."""
    result = _run(tmp_path, [OK_BLOCK], scripts=["fetch_orphan.py"])
    assert any("fetch_orphan.py is not referenced" in n for n in result.notices)
