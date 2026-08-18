from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location(
    "research_protein_trait", REPO_ROOT / "scripts" / "research_protein_trait.py"
)
assert SPEC and SPEC.loader
rpt = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = rpt
SPEC.loader.exec_module(rpt)


def test_resolve_record_by_unique_path_and_identifier():
    path = REPO_ROOT / "data" / "traits" / "structure" / "cavity" / "pocket.yaml"
    assert rpt.resolve_record(str(path)) == path.resolve()
    assert rpt.resolve_record("proteintraitsmech:POCKET") == path


def test_template_vars_capture_protein_trait_context():
    path = REPO_ROOT / "data" / "traits" / "structure" / "cavity" / "pocket.yaml"
    variables = rpt.template_vars(rpt.load_record(path), path)
    assert variables["trait_identifier"] == "proteintraitsmech:POCKET"
    assert variables["trait_axis"] == "STRUCTURE"
    assert variables["record_path"].endswith("structure/cavity/pocket.yaml")


def test_build_command_uses_provider_and_citation_sidecar(tmp_path):
    command = rpt.build_command(
        "asta",
        REPO_ROOT / "templates" / "protein_trait_mechanism_research.md",
        tmp_path / "report.md",
        tmp_path / "report.md.citations.md",
        {"trait_label": "pocket"},
        ["--param", "top_k=10"],
    )
    assert command[:4] == [
        "deep-research-client",
        "research",
        "--template",
        "templates/protein_trait_mechanism_research.md",
    ]
    assert ["--provider", "asta"] == command[
        command.index("--provider") : command.index("--provider") + 2
    ]
    assert "--separate-citations" in command
    assert command[-2:] == ["--param", "top_k=10"]


def test_edison_alias_and_platform_key(monkeypatch):
    assert rpt.canonical_provider("Edison") == "falcon"
    monkeypatch.delenv("EDISON_API_KEY", raising=False)
    monkeypatch.setenv("EDISON_PLATFORM_API_KEY", "test-only")
    assert rpt.research_env()["EDISON_API_KEY"] == "test-only"
