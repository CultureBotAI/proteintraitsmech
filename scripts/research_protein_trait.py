#!/usr/bin/env python3
"""Run provider-based deep research for one ProteinTraitsMech record."""

from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent
TRAITS_DIR = REPO_ROOT / "data" / "traits"
DEFAULT_TEMPLATE = REPO_ROOT / "templates" / "protein_trait_mechanism_research.md"
DEFAULT_RESEARCH_DIR = REPO_ROOT / "research"
PROVIDER_ALIASES = {"edison": "falcon", "futurehouse": "falcon"}


def load_record(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Protein trait file is not a YAML mapping: {path}")
    return data


def resolve_record(target: str) -> Path:
    candidate = Path(target)
    for path in (candidate, REPO_ROOT / candidate):
        if path.is_file():
            return path.resolve()

    files = sorted(TRAITS_DIR.rglob("*.yaml"))
    stem_matches = [path for path in files if path.stem.casefold() == target.casefold()]
    if len(stem_matches) == 1:
        return stem_matches[0]
    if len(stem_matches) > 1:
        choices = ", ".join(
            str(path.relative_to(REPO_ROOT)) for path in stem_matches[:20]
        )
        raise ValueError(
            f"Ambiguous protein trait slug {target!r}: {choices}; pass a path"
        )

    field_matches = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        if target.casefold() not in text.casefold():
            continue
        record = load_record(path)
        if any(
            str(record.get(field, "")).casefold() == target.casefold()
            for field in ("identifier", "label")
        ):
            field_matches.append(path)
    if len(field_matches) == 1:
        return field_matches[0]
    if len(field_matches) > 1:
        choices = ", ".join(
            str(path.relative_to(REPO_ROOT)) for path in field_matches[:20]
        )
        raise ValueError(
            f"Ambiguous protein trait target {target!r}: {choices}; pass a path"
        )
    raise FileNotFoundError(
        f"Protein trait target not found under {TRAITS_DIR}: {target}"
    )


def _summary(value: Any, limit: int = 6000) -> str:
    if value in (None, [], {}):
        return "None recorded"
    if isinstance(value, str):
        text = value
    else:
        text = yaml.safe_dump(value, sort_keys=False, allow_unicode=True).strip()
    return text if len(text) <= limit else text[:limit] + "\n... (truncated)"


def template_vars(record: dict[str, Any], path: Path) -> dict[str, str]:
    graphs = record.get("causal_graphs") or []
    graph_summary = []
    for graph in graphs:
        if isinstance(graph, dict):
            graph_summary.append(
                f"{graph.get('graph_id') or graph.get('title')}: "
                f"{len(graph.get('nodes') or [])} nodes, {len(graph.get('edges') or [])} edges"
            )
    return {
        "record_path": str(path.relative_to(REPO_ROOT)),
        "trait_identifier": str(record.get("identifier", "")),
        "trait_label": str(record.get("label", path.stem)),
        "trait_axis": str(record.get("trait_axis", "")),
        "trait_category": str(record.get("trait_category", "")),
        "term_kind": str(record.get("term_kind", "")),
        "mapping_status": str(record.get("mapping_status", "")),
        "definition": str(record.get("definition", "")),
        "definitions": _summary(record.get("definitions")),
        "synonyms": _summary(record.get("synonyms")),
        "parent_traits": _summary(record.get("parent_traits")),
        "xrefs": _summary(record.get("xrefs")),
        "mapped_xrefs": _summary(record.get("mapped_xrefs")),
        "chemical_participants": _summary(record.get("chemical_participants")),
        "canonical_examples": _summary(record.get("canonical_examples")),
        "trait_relations": _summary(record.get("trait_relations")),
        "causal_graph_summary": "; ".join(graph_summary) or "None recorded",
        "existing_evidence": _summary(record.get("evidence")),
    }


def canonical_provider(provider: str) -> str:
    key = provider.casefold()
    return PROVIDER_ALIASES.get(key, key)


def provider_args(provider: str) -> list[str]:
    return ["--use-cborg"] if provider == "cborg" else ["--provider", provider]


def research_env() -> dict[str, str]:
    env = os.environ.copy()
    if not env.get("EDISON_API_KEY"):
        for alias in ("EDISON_PLATFORM_API_KEY", "FUTUREHOUSE_API_KEY"):
            if env.get(alias):
                env["EDISON_API_KEY"] = env[alias]
                break
    return env


def build_command(
    provider: str,
    template: Path,
    output: Path,
    citations: Path,
    variables: dict[str, str],
    passthrough: list[str],
    client_command: str = "deep-research-client",
) -> list[str]:
    try:
        template_arg = str(template.resolve().relative_to(REPO_ROOT))
    except ValueError:
        template_arg = str(template.resolve())
    command = [client_command, "research", "--template", template_arg]
    for key, value in variables.items():
        command.extend(["--var", f"{key}={value}"])
    command.extend(provider_args(provider))
    command.extend(
        [
            "--output",
            str(output.resolve()),
            "--separate-citations",
            str(citations.resolve()),
        ]
    )
    command.extend(passthrough)
    return command


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", default="falcon")
    parser.add_argument(
        "--target", required=True, help="YAML path, unique slug, identifier, or label"
    )
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    parser.add_argument("--research-dir", type=Path, default=DEFAULT_RESEARCH_DIR)
    parser.add_argument("--client-command", default="deep-research-client")
    parser.add_argument("--dry-run", action="store_true")
    args, passthrough = parser.parse_known_args(argv)
    args.passthrough = passthrough
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    provider = canonical_provider(args.provider)
    record_path = resolve_record(args.target)
    record = load_record(record_path)
    relative = record_path.relative_to(TRAITS_DIR)
    output_dir = args.research_dir / "traits" / relative.parent
    output = output_dir / f"{relative.stem}-deep-research-{provider}.md"
    citations = output.with_suffix(output.suffix + ".citations.md")
    variables = template_vars(record, record_path)
    command = build_command(
        provider,
        args.template,
        output,
        citations,
        variables,
        args.passthrough,
        args.client_command,
    )
    print(f"Researching: {variables['trait_label']} ({provider}) -> {output}")
    if args.dry_run:
        print(shlex.join(command))
        return 0
    output_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(command, check=True, cwd=REPO_ROOT, env=research_env())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
