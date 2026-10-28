"""Reviewed structural-trait fields shared by seeders and the guarded editor.

The ledger pins both inspected record bytes and each maintained seeder's original
emission. Unexpected changes require another review. This module only transforms
text; it cannot qualify examples, allocate identifiers, or write trait records.
"""

from __future__ import annotations

import hashlib
import re
from functools import lru_cache
from pathlib import Path

import yaml

from record_io import extract_block, replace_block, top_level_keys

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "data/curation/structural_trait_curations.yaml"
FIELDS = {
    "definition", "definition_source", "definitions", "synonyms", "parent_traits",
    "xrefs", "trait_relations", "detection_methods", "secondary_structure_representations",
    "structural_geometry_representations", "evidence", "license", "mapping_status",
    "curation_history", "discussions", "causal_graphs",
}


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def parse_record(text: str) -> dict:
    keys = top_level_keys(text)
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate top-level record keys")
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError("record must be a mapping")
    return data


@lru_cache(maxsize=1)
def load_curations() -> dict[str, dict]:
    data = yaml.safe_load(LEDGER.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("version") != 1:
        raise ValueError("unsupported structural curation ledger")
    records = data.get("records")
    if not isinstance(records, list) or not records:
        raise ValueError("curation ledger must contain records")
    result: dict[str, dict] = {}
    paths: set[str] = set()
    for entry in records:
        identifier = entry["identifier"]
        path = Path(entry["path"])
        if (identifier in result or entry["path"] in paths or path.is_absolute()
                or ".." in path.parts or path.suffix != ".yaml"
                or path.parts[:3] != ("data", "traits", "structure")):
            raise ValueError(f"duplicate or unsafe curation target: {identifier}")
        for key in ("input_sha256", "output_sha256"):
            if not re.fullmatch(r"[0-9a-f]{64}", entry[key]):
                raise ValueError(f"invalid {key}: {identifier}")
        if (entry.get("allow_proposed_followup") is True
                and entry.get("prior_output_sha256") != entry["input_sha256"]):
            raise ValueError(f"follow-up must pin its prior output: {identifier}")
        if not entry.get("seed_preimages"):
            raise ValueError(f"missing maintained seeder: {identifier}")
        for owner, sha in entry["seed_preimages"].items():
            if (not re.fullmatch(r"seed_[a-z_]+", owner)
                    or not re.fullmatch(r"[0-9a-f]{64}", sha)):
                raise ValueError(f"invalid seeder pin: {identifier}")
        blocks = entry["blocks"]
        if not isinstance(blocks, dict) or not blocks or set(blocks) - FIELDS:
            raise ValueError(f"unreviewed field in curation: {identifier}")
        for key, block in blocks.items():
            if block is None:
                continue
            parsed = yaml.safe_load(block)
            if not isinstance(parsed, dict) or set(parsed) != {key}:
                raise ValueError(f"invalid field block {key}: {identifier}")
        if yaml.safe_load(blocks.get("mapping_status", "{}")) != {
            "mapping_status": "PROPOSED"
        }:
            raise ValueError(f"agent curation must remain PROPOSED: {identifier}")
        events = yaml.safe_load(blocks.get("curation_history", "{}")).get("curation_history")
        if (not events or not events[-1].get("llm_assisted")
                or events[-1].get("curator") != "codex-gpt-6-astra"):
            raise ValueError(f"missing honest agent attribution: {identifier}")
        paths.add(entry["path"])
        result[identifier] = entry
    return result


def apply_blocks(text: str, entry: dict) -> str:
    data = parse_record(text)
    if (data.get("identifier") != entry["identifier"]
            or data.get("trait_axis") != "STRUCTURE"
            or data.get("trait_category") != entry["trait_category"]
            or data.get("term_kind") != "CLASS"):
        raise ValueError("unexpected structural trait identity/scope")
    expected = dict(data)
    old_history = data.get("curation_history") or []
    new_history = yaml.safe_load(entry["blocks"]["curation_history"])["curation_history"]
    if new_history[:len(old_history)] != old_history:
        raise ValueError("existing curation history must be preserved unchanged")
    out = text
    for key, block in entry["blocks"].items():
        previous = extract_block(out, key) or ""
        lines = previous.splitlines(keepends=True)
        end = len(lines)
        while end and (not lines[end - 1].strip() or lines[end - 1].lstrip().startswith("#")):
            end -= 1
        trailing_comments = "".join(lines[end:]) if any(
            line.lstrip().startswith("#") for line in lines[end:]
        ) else ""
        if block is None:
            expected.pop(key, None)
            if key in data:
                out = replace_block(out, key, trailing_comments)
        else:
            expected[key] = yaml.safe_load(block)[key]
            out = replace_block(out, key, block.rstrip("\n") + "\n" + trailing_comments)
    if parse_record(out) != expected:
        raise ValueError("curation changed fields outside the reviewed blocks")
    return out


def curate_seed(text: str, owner: str) -> str:
    """Apply only an explicitly pinned source emission; leave other seeds intact."""
    identifier = parse_record(text).get("identifier")
    entry = load_curations().get(identifier)
    if entry is None:
        return text
    expected = entry["seed_preimages"].get(owner)
    if expected is None or digest(text) != expected:
        raise ValueError(f"{identifier}: {owner} source drift; re-review required")
    return apply_blocks(text, entry)
