#!/usr/bin/env python3
"""Repair the unreceipted durable UniProt grounding generation.

This is a narrow, one-off bridge for the historical Batch-001 state: three
hard-invalid examples are pruned, four exact InterPro head-slice definitions are
restored to the full pinned InterPro 109.0 abstracts, and the complete
post-prune durable evidence registry receives fail-closed
``qualified_record_bindings.jsonl`` receipts.

The transaction deliberately reuses the same content-gate receipt shape and
validated record writer as ``ground_uniprot_examples.py promote``.  Dry-run is
the default; ``--apply`` atomically installs the pruned durable registries, the
new receipt image, and any repaired trait records with in-process rollback.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

import ground_uniprot_examples as ground  # noqa: E402
import uniprot_record_content_gate as content_gate  # noqa: E402
from record_io import replace_block, write_validated_record  # noqa: E402
from uniprot_record_content_gate import _collapse, _load_interpro  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]

REPAIRED_INTERPRO_DEFINITIONS = {
    (
        "data/traits/sequence/family/hamap/"
        "dna-directed-rna-polymerase-subunit-rpo5-rpo5-mf_00025.yaml"
    ): "IPR014381",
    (
        "data/traits/sequence/family/hamap/"
        "n-acetyl-gamma-glutamyl-phosphate-reductase-argc-mf_00150.yaml"
    ): "IPR000706",
    (
        "data/traits/sequence/family/panther/"
        "peripheral-type-benzodiazepine-receptor-pthr10057.yaml"
    ): "IPR004307",
    (
        "data/traits/sequence/family/panther/"
        "secretoglobin-family-1-member-pthr10136.yaml"
    ): "IPR043215",
}

PRUNED_EVIDENCE_IDS = frozenset(
    {
        "ug-evidence:0feb9d116e5a2ecf6df3b5fdc2f58df73a11e7b611980cc57cbcf1ebbd6ee316",
        "ug-evidence:1a487ebe82e0adccdff426300d7aa252eb84e28b9cfbfc2d2561b4057cd1dbf1",
        "ug-evidence:6c24aa24f408a1a66ae25dfa98fbc29e52f41ef7cc2d43973684d3cce3a88a7d",
    }
)


class RepairError(ValueError):
    """The durable registry cannot be repaired safely."""


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _remove_top_level_block(text: str, key: str) -> str:
    lines = text.splitlines(keepends=True)
    start = next((i for i, line in enumerate(lines) if line.startswith(f"{key}:")), None)
    if start is None:
        return text
    end = start + 1
    while end < len(lines):
        line = lines[end]
        if line.strip() and not line.startswith((" ", "\t", "-")):
            break
        end += 1
    return "".join(lines[:start] + lines[end:])


def _safe_trait_path(rel_path: str, traits_root: Path) -> Path:
    path = (REPO_ROOT / rel_path).resolve()
    try:
        path.relative_to(traits_root.resolve())
    except ValueError as exc:
        raise RepairError(f"repair target is outside the trait root: {rel_path}") from exc
    return path


def _rg_paths(patterns: list[str], root: Path) -> list[Path]:
    if not patterns:
        return []
    executable = shutil.which("rg")
    if executable is None:
        compiled = [re.compile(pattern) for pattern in patterns]
        matches: list[Path] = []
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if any(pattern.search(text) for pattern in compiled):
                matches.append(path.resolve())
        return sorted(matches)
    command = [
        executable,
        "-l",
        "--no-ignore",
        "--hidden",
    ]
    for pattern in patterns:
        command.extend(["-e", pattern])
    command.append(str(root))
    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode not in {0, 1}:
        raise RepairError(result.stderr.strip() or "rg failed while listing evidence paths")
    return sorted(Path(line).resolve() for line in result.stdout.splitlines() if line)


def _repair_interpro_definitions(
    texts: dict[Path, str],
    *,
    traits_root: Path,
) -> dict[str, int]:
    entries, _, _ = _load_interpro(
        content_gate.DEFAULT_INTERPRO_XML,
        content_gate.INTERPRO_109_XML_SHA256,
        set(REPAIRED_INTERPRO_DEFINITIONS.values()),
        set(),
        set(),
        set(),
    )
    changed = 0
    lengths: dict[str, int] = {}
    for rel_path, interpro_id in REPAIRED_INTERPRO_DEFINITIONS.items():
        path = _safe_trait_path(rel_path, traits_root)
        text = texts.setdefault(path, path.read_text(encoding="utf-8"))
        record = yaml.safe_load(text)
        if not isinstance(record, dict):
            raise RepairError(f"{rel_path}: record is not a YAML mapping")
        full = _collapse(entries[interpro_id].abstract)
        current = record.get("definition")
        if not isinstance(current, str):
            raise RepairError(f"{rel_path}: definition is not text")
        lengths[interpro_id] = len(full)
        if current == full:
            continue
        historical = _collapse(full[:1800])
        if current.rstrip() != historical:
            raise RepairError(
                f"{rel_path}: definition is not the exact historical InterPro head slice"
            )
        matching_rows = [
            row
            for row in record.get("definitions") or []
            if isinstance(row, dict)
            and row.get("source") == record.get("definition_source")
        ]
        if len(matching_rows) != 1 or matching_rows[0].get("text") != current:
            raise RepairError(
                f"{rel_path}: paired definitions[] row does not match the definition"
            )
        occurrences = text.count(current)
        if occurrences != 2:
            raise RepairError(
                f"{rel_path}: historical definition occurs {occurrences} time(s), "
                "expected exactly two"
            )
        texts[path] = text.replace(current, full)
        changed += 1
    return {"records_changed": changed, **lengths}


def _prune_invalid_examples(
    texts: dict[Path, str],
    evidence: dict[str, dict[str, Any]],
    *,
    traits_root: Path,
) -> dict[str, Any]:
    pruned_rows = {eid: evidence[eid] for eid in sorted(PRUNED_EVIDENCE_IDS)}
    by_trait = {row["trait_id"]: eid for eid, row in pruned_rows.items()}
    remaining = set(PRUNED_EVIDENCE_IDS)
    changed_paths: set[Path] = set()
    for path in _rg_paths(sorted(remaining), traits_root):
        text = texts.get(path)
        if text is None:
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError as exc:
                raise RepairError(f"{path}: cannot read YAML as UTF-8") from exc
        if not any(eid in text for eid in remaining):
            continue
        record = yaml.safe_load(text)
        if not isinstance(record, dict):
            raise RepairError(f"{path}: record is not a YAML mapping")
        before = copy.deepcopy(record.get("canonical_examples") or [])
        after = []
        for example in before:
            if not isinstance(example, dict):
                after.append(example)
                continue
            occurrences = []
            for occurrence in example.get("trait_occurrences") or []:
                evidence_id = (
                    occurrence.get("source_evidence_id")
                    if isinstance(occurrence, dict)
                    else None
                )
                if evidence_id in remaining:
                    row = pruned_rows[evidence_id]
                    if (
                        record.get("identifier") != row.get("trait_id")
                        or occurrence.get("protein_id") != row.get("protein_id")
                    ):
                        raise RepairError(
                            f"{path}: pruned occurrence {evidence_id} does not match "
                            "the durable evidence row"
                        )
                    remaining.remove(evidence_id)
                    continue
                occurrences.append(occurrence)
            if occurrences:
                updated = copy.deepcopy(example)
                updated["trait_occurrences"] = occurrences
                after.append(updated)
        updated_record = dict(record)
        if after:
            updated_record["canonical_examples"] = after
            texts[path] = replace_block(
                text,
                "canonical_examples",
                yaml.safe_dump(
                    {"canonical_examples": after},
                    sort_keys=False,
                    allow_unicode=True,
                    width=100,
                ),
            )
        else:
            updated_record.pop("canonical_examples", None)
            texts[path] = _remove_top_level_block(text, "canonical_examples")
        reparsed = yaml.safe_load(texts[path])
        if reparsed != updated_record:
            raise RepairError(f"{path}: pruned canonical_examples splice changed other fields")
        changed_paths.add(path)
    if remaining:
        raise RepairError(
            "could not find installed occurrence(s) for pruned evidence: "
            + ", ".join(sorted(remaining))
        )
    return {
        "records_changed": len(changed_paths),
        "evidence_ids": sorted(PRUNED_EVIDENCE_IDS),
        "traits": dict(sorted(by_trait.items())),
    }


def _rg_source_evidence_paths(traits_root: Path) -> list[Path]:
    return _rg_paths(["source_evidence_id: ug-evidence:"], traits_root)


def _installed_records(
    texts: dict[Path, str],
    evidence: dict[str, dict[str, Any]],
    *,
    traits_root: Path,
) -> dict[str, tuple[Path, str, dict[str, Any]]]:
    by_evidence: dict[str, tuple[Path, str, dict[str, Any]]] = {}
    for path in _rg_source_evidence_paths(traits_root):
        text = texts.get(path, path.read_text(encoding="utf-8"))
        record = yaml.safe_load(text)
        if not isinstance(record, dict):
            raise RepairError(f"{path}: record is not a YAML mapping")
        for example in record.get("canonical_examples") or []:
            if not isinstance(example, dict):
                continue
            for occurrence in example.get("trait_occurrences") or []:
                if not isinstance(occurrence, dict):
                    continue
                evidence_id = occurrence.get("source_evidence_id")
                if evidence_id not in evidence:
                    continue
                if evidence_id in by_evidence:
                    first = by_evidence[evidence_id][0]
                    raise RepairError(
                        f"{evidence_id}: duplicate installed occurrence in "
                        f"{ground._display_path(first)} and {ground._display_path(path)}"
                    )
                by_evidence[evidence_id] = (path, text, record)
    missing = sorted(set(evidence) - set(by_evidence))
    if missing:
        raise RepairError(
            "could not dereference durable evidence from trait records after repair: "
            + ", ".join(missing[:5])
        )
    return by_evidence


def _interpro_intervals_by_evidence(
    evidence: dict[str, dict[str, Any]], interpro_frame: Path
) -> dict[str, list[dict[str, int]]]:
    raw = json.loads(interpro_frame.read_text(encoding="utf-8"))
    proteins = raw.get("proteins")
    if not isinstance(proteins, dict):
        raise RepairError(f"{interpro_frame}: missing proteins mapping")
    intervals_by_evidence: dict[str, list[dict[str, int]]] = {}
    for evidence_id, row in sorted(evidence.items()):
        if row.get("provider_kind") != "INTERPRO":
            continue
        accession = str(row.get("protein_id") or "").split(":", 1)[-1]
        source_trait_id = str(row.get("source_trait_id") or "")
        intervals, reasons = ground._normalise_intervals(
            proteins.get(accession, {}).get(source_trait_id)
            if isinstance(proteins.get(accession), dict)
            else None
        )
        if not intervals or reasons:
            raise RepairError(
                f"{evidence_id}: cannot replay InterPro intervals for "
                f"{row.get('protein_id')} {source_trait_id}"
            )
        if ground._value_digest(intervals) != row.get("provider_entry_sha256"):
            raise RepairError(
                f"{evidence_id}: replayed InterPro intervals do not match the durable "
                "provider_entry_sha256"
            )
        intervals_by_evidence[evidence_id] = intervals
    return intervals_by_evidence


def _candidate_for_evidence(
    evidence: dict[str, Any],
    protein: dict[str, Any],
    intervals: list[dict[str, int]],
) -> dict[str, Any]:
    identity = {
        "trait_id": evidence.get("trait_id"),
        "protein_id": evidence.get("protein_id"),
        "source_trait_id": evidence.get("source_trait_id"),
        "mapping_method": evidence.get("mapping_method"),
        "evidence_source": evidence.get("evidence_source"),
        "source_release": evidence.get("source_release"),
        "sequence_release": protein.get("uniprot_release"),
        "sequence_sha256": evidence.get("sequence_sha256"),
        "scope": evidence.get("scope"),
        "coordinate_frame": evidence.get("coordinate_frame"),
        "intervals": intervals,
        "residue_positions": copy.deepcopy(evidence.get("residue_positions") or []),
        "structure_id": evidence.get("structure_id"),
        "chain_id": evidence.get("chain_id"),
        "ecod_domain_id": evidence.get("ecod_domain_id"),
        "sifts_mapping_id": evidence.get("sifts_mapping_id"),
    }
    return {
        **identity,
        "candidate_id": ground.derive_candidate_id(identity),
        "sequence_length": protein["sequence_length"],
    }


def _gate_args(args: argparse.Namespace) -> SimpleNamespace:
    return SimpleNamespace(
        interpro_xml=args.interpro_xml,
        interpro_xml_sha256=args.interpro_xml_sha256,
        pfam_clans=args.pfam_clans,
        pfam_clans_sha256=args.pfam_clans_sha256,
        pfam_types=args.pfam_types,
        pfam_types_sha256=args.pfam_types_sha256,
        panther_classifications=args.panther_classifications,
        panther_classifications_sha256=args.panther_classifications_sha256,
    )


def _build_bindings(
    evidence: dict[str, dict[str, Any]],
    proteins: dict[str, dict[str, Any]],
    records: dict[str, tuple[Path, str, dict[str, Any]]],
    intervals_by_evidence: dict[str, list[dict[str, int]]],
    args: argparse.Namespace,
) -> dict[str, dict[str, Any]]:
    gate_args = _gate_args(args)
    content_records = {
        path: record for path, _text, record in records.values()
    }
    gate = ground._prepare_content_gate(content_records.values(), gate_args)
    bindings: dict[str, dict[str, Any]] = {}
    blocked: list[str] = []
    for evidence_id, row in sorted(evidence.items()):
        protein_id = str(row.get("protein_id") or "")
        protein = proteins.get(protein_id)
        if protein is None:
            raise RepairError(f"{evidence_id}: missing ProteinReference {protein_id!r}")
        path, text, record = records[evidence_id]
        candidate = _candidate_for_evidence(
            row,
            protein,
            intervals_by_evidence.get(evidence_id, []),
        )
        projection, findings = ground._content_gate_projection(gate, record, candidate, gate_args)
        hard_codes = sorted(
            finding.code
            for finding in findings
            if finding.severity == ground.CONTENT_GATE_HARD
        )
        if hard_codes:
            blocked.append(
                f"{candidate['candidate_id']}: {','.join(hard_codes)} "
                f"({ground._display_path(path)})"
            )
        bindings[evidence_id] = ground._qualified_record_binding(
            evidence_id=evidence_id,
            candidate_id=candidate["candidate_id"],
            trait_id=str(row["trait_id"]),
            record_path=path,
            record_sha256=_sha256_text(text),
            content_gate_projection=projection,
        )
    if blocked:
        raise RepairError(
            "post-repair content gate still rejects durable claim(s):\n  "
            + "\n  ".join(blocked[:10])
        )
    return bindings


def _install_transaction(
    artifact_updates: list[tuple[Path, str]],
    trait_updates: dict[Path, str],
) -> None:
    targets = [path.resolve() for path, _text in artifact_updates]
    targets.extend(path.resolve() for path in sorted(trait_updates))
    if len(targets) != len(set(targets)):
        raise RepairError("repair transaction contains duplicate output paths")
    snapshots = {
        path: path.read_bytes() if path.is_file() else None
        for path in targets
    }
    attempted: list[Path] = []
    try:
        for path, text in artifact_updates:
            target = path.resolve()
            attempted.append(target)
            ground._atomic_text(target, text)
        for path, text in sorted(trait_updates.items()):
            target = path.resolve()
            attempted.append(target)
            write_validated_record(target, text, encoding="utf-8")
    except Exception as exc:
        rollback_errors: list[str] = []
        for path in reversed(attempted):
            try:
                snapshot = snapshots[path]
                if snapshot is None:
                    path.unlink(missing_ok=True)
                else:
                    ground._atomic_bytes(path, snapshot)
            except Exception as rollback_exc:  # pragma: no cover - catastrophic I/O path
                rollback_errors.append(f"{path}: {rollback_exc}")
        if rollback_errors:
            raise RepairError(
                "repair transaction failed and rollback was incomplete: "
                + "; ".join(rollback_errors[:5])
            ) from exc
        raise RepairError(f"repair transaction failed and was rolled back: {exc}") from exc


def run(args: argparse.Namespace) -> int:
    traits_root = args.traits.resolve()
    protein_digest = ground._artifact_digest(args.durable_protein_registry)
    evidence_digest = ground._artifact_digest(args.durable_evidence_registry)
    bindings_digest = ground._artifact_digest(args.durable_qualified_record_bindings)
    if bindings_digest is not None:
        raise RepairError(
            f"durable qualified-record binding registry already exists: "
            f"{args.durable_qualified_record_bindings}"
        )

    proteins = ground._semantic_registry(args.durable_protein_registry)
    evidence = ground._semantic_evidence_registry(args.durable_evidence_registry)
    missing_pruned = sorted(PRUNED_EVIDENCE_IDS - set(evidence))
    if missing_pruned:
        raise RepairError(
            "durable evidence is not the expected unrepaired state; missing pruned "
            f"evidence IDs: {missing_pruned}"
        )

    original_texts: dict[Path, str] = {}
    repaired_texts = dict(original_texts)
    definition_summary = _repair_interpro_definitions(
        repaired_texts,
        traits_root=traits_root,
    )
    prune_summary = _prune_invalid_examples(
        repaired_texts,
        evidence,
        traits_root=traits_root,
    )

    repaired_evidence = {
        evidence_id: row
        for evidence_id, row in evidence.items()
        if evidence_id not in PRUNED_EVIDENCE_IDS
    }
    used_proteins = {
        str(row["protein_id"])
        for row in repaired_evidence.values()
    }
    repaired_proteins = {
        protein_id: row
        for protein_id, row in proteins.items()
        if protein_id in used_proteins
    }
    ground._validate_registry_mapping(
        repaired_proteins,
        args.durable_protein_registry,
    )
    ground._validate_evidence_mapping(
        repaired_evidence,
        args.durable_evidence_registry,
    )
    ground._validate_registry_links(repaired_proteins, repaired_evidence)

    installed = _installed_records(
        repaired_texts,
        repaired_evidence,
        traits_root=traits_root,
    )
    intervals_by_evidence = _interpro_intervals_by_evidence(
        repaired_evidence,
        args.interpro_frame,
    )
    bindings = _build_bindings(
        repaired_evidence,
        repaired_proteins,
        installed,
        intervals_by_evidence,
        args,
    )
    if set(bindings) != set(repaired_evidence):
        raise RepairError("qualified-record bindings do not cover repaired evidence exactly")

    trait_updates = {
        path: text
        for path, text in repaired_texts.items()
        if _sha256_text(path.read_text(encoding="utf-8")) != _sha256_text(text)
    }
    trait_preimages = {
        path: _sha256_text(path.read_text(encoding="utf-8"))
        for path in trait_updates
    }
    protein_text = ground._registry_text(repaired_proteins)
    evidence_text = ground._registry_text(repaired_evidence)
    bindings_text = ground._registry_text(bindings)
    artifact_updates = [
        (args.durable_protein_registry, protein_text),
        (args.durable_evidence_registry, evidence_text),
        (args.durable_qualified_record_bindings, bindings_text),
    ]

    source_counts = Counter(row.get("provider_kind") for row in repaired_evidence.values())
    action = "APPLY" if args.apply else "DRY-RUN"
    print(
        f"{action}: {len(PRUNED_EVIDENCE_IDS):,} hard-invalid evidence row(s) pruned; "
        f"{len(repaired_proteins):,} protein(s), {len(repaired_evidence):,} evidence "
        f"row(s), {len(bindings):,} qualified-record binding(s); "
        f"{len(trait_updates):,} trait record(s) changed"
    )
    print(
        "retained evidence by provider: "
        + ", ".join(f"{key}={value}" for key, value in sorted(source_counts.items()))
    )
    print(
        f"definition repairs changed {definition_summary['records_changed']} record(s); "
        f"example pruning changed {prune_summary['records_changed']} record(s)"
    )
    if not args.apply:
        print("No durable registries or trait records written; pass --apply to install.")
        return 0

    current_protein_digest = ground._artifact_digest(args.durable_protein_registry)
    current_evidence_digest = ground._artifact_digest(args.durable_evidence_registry)
    current_bindings_digest = ground._artifact_digest(args.durable_qualified_record_bindings)
    if (
        current_protein_digest != protein_digest
        or current_evidence_digest != evidence_digest
        or current_bindings_digest != bindings_digest
    ):
        raise RepairError("durable registry artifact(s) changed during repair preflight")
    changed_records = [
        path
        for path, expected_sha in trait_preimages.items()
        if _sha256_text(path.read_text(encoding="utf-8")) != expected_sha
    ]
    if changed_records:
        raise RepairError(
            "record(s) changed during repair preflight: "
            + ", ".join(ground._display_path(path) for path in sorted(changed_records)[:5])
        )

    _install_transaction(artifact_updates, trait_updates)
    print(
        f"WROTE 3 durable grounding artifact(s) and {len(trait_updates):,} "
        "trait record(s)"
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--traits", type=Path, default=ground.DEFAULT_TRAITS)
    parser.add_argument(
        "--durable-protein-registry",
        type=Path,
        default=ground.DEFAULT_DURABLE_PROTEIN_REGISTRY,
    )
    parser.add_argument(
        "--durable-evidence-registry",
        type=Path,
        default=ground.DEFAULT_DURABLE_EVIDENCE_REGISTRY,
    )
    parser.add_argument(
        "--durable-qualified-record-bindings",
        type=Path,
        default=ground.DEFAULT_DURABLE_QUALIFIED_RECORD_BINDINGS,
    )
    parser.add_argument("--interpro-frame", type=Path, default=ground.DEFAULT_INTERPRO_FRAME)
    parser.add_argument("--interpro-xml", type=Path, default=content_gate.DEFAULT_INTERPRO_XML)
    parser.add_argument(
        "--interpro-xml-sha256",
        default=content_gate.INTERPRO_109_XML_SHA256,
    )
    parser.add_argument("--pfam-clans", type=Path, default=content_gate.DEFAULT_PFAM_CLANS)
    parser.add_argument(
        "--pfam-clans-sha256",
        default=content_gate.PFAM_A_CLANS_SHA256,
    )
    parser.add_argument("--pfam-types", type=Path, default=content_gate.DEFAULT_PFAM_TYPES)
    parser.add_argument("--pfam-types-sha256", default=content_gate.PFAM_TYPES_SHA256)
    parser.add_argument(
        "--panther-classifications",
        type=Path,
        default=content_gate.DEFAULT_PANTHER_CLASSIFICATIONS,
    )
    parser.add_argument(
        "--panther-classifications-sha256",
        default=content_gate.PANTHER_19_CLASSIFICATIONS_SHA256,
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        return run(args)
    except RepairError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
