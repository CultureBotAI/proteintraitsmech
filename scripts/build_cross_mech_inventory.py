#!/usr/bin/env python3
"""Build a protein-first, read-only cross-Mech index; never qualify an example.

Unlike the pair audit, this includes every discovered protein, even when its
sibling role is a target, reference, or unclassified. Existing PTM examples are
joined by exact accession, including isoforms. Generic feature tracks remain
separate from record-specific, qualified trait occurrences.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from urllib.parse import quote

import yaml

import cross_mech_proteins as cm
from docs_protein_sequences import ProteinSequenceRegistry
from validate_uniprot_grounding import RELEASE_RE, SEQUENCE_RE

ROOT = Path(__file__).resolve().parents[1]
PTM_URL = "https://github.com/CultureBotAI/proteintraitsmech/blob/main/"
OUTPUTS = ("protein_inventory.jsonl", "protein_sequences.jsonl", "coverage.json", "coverage.md")


def digest(path: Path) -> str:
    checksum = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            checksum.update(chunk)
    return checksum.hexdigest()


def matching_records(traits: Path, proteins: set[str]) -> list[Path]:
    """Content prefilter only; YAML/exact equality decides example membership.

    Hidden and ignored records are deliberately included. No inference from a
    substring match, reference, label, or prefix (canonical vs isoform) is made.
    """
    if not proteins:
        return []
    executable = shutil.which("rg")
    if executable is None:
        # os.walk includes hidden/ignored paths. Do not silently treat an
        # unreadable directory or file as evidence that no example exists.
        def fail(error: OSError) -> None:
            raise error

        pattern = re.compile(b"|".join(re.escape(p.encode("utf-8")) for p in sorted(proteins)))
        matches = []
        try:
            for directory, _, filenames in os.walk(traits, onerror=fail, followlinks=False):
                for filename in filenames:
                    path = Path(directory) / filename
                    if path.suffix in {".yaml", ".yml"} and not path.is_symlink():
                        if pattern.search(path.read_bytes()):
                            matches.append(path)
        except OSError as error:
            raise cm.CrossMechError(f"trait search failed: {error}") from error
        return sorted(matches)
    result = subprocess.run(
        [executable, "--no-config", "--hidden", "--no-ignore", "-l", "-0", "-F", "-f", "-",
         "-g", "*.yaml", "-g", "*.yml", str(traits)],
        input="\n".join(sorted(proteins)) + "\n", text=True, capture_output=True,
    )
    if result.returncode not in (0, 1):
        raise cm.CrossMechError(f"trait search failed: {result.stderr.strip()}")
    return sorted(Path(value) for value in result.stdout.split("\0") if value)


def load_frame(path: Path | None) -> tuple[dict, dict]:
    if path is None:
        return {}, {}
    # An explicitly supplied but missing/malformed cache is not an empty one.
    blob = json.loads(path.read_text(encoding="utf-8"))
    meta = blob.get("_meta", {})
    if (meta.get("source") != "UniProt" or meta.get("schema") != 1
            or not RELEASE_RE.fullmatch(str(meta.get("release", "")))
            or not isinstance(blob.get("proteins"), dict)):
        raise cm.CrossMechError("residue frame must be a release-stamped UniProt sidecar")
    return blob["proteins"], meta


def sequence_payload(protein: str, reference: dict | None, frame: dict, meta: dict) -> dict | None:
    entry = frame.get(protein.removeprefix("UniProtKB:")) or {}
    seq = reference["sequence"] if reference else entry.get("seq", "")
    if not seq or not SEQUENCE_RE.fullmatch(seq):
        return None
    release = reference["uniprot_release"] if reference else meta.get("release")
    result = {
        "protein_id": protein, "sequence": seq, "sequence_length": len(seq),
        "sequence_sha256": hashlib.sha256(seq.encode("ascii")).hexdigest(),
        "uniprot_release": release,
        "sequence_source": "ProteinReference" if reference else "UniProt residue-frame discovery",
        "generic_features": [], "annotation_limitations": [],
    }
    if reference and "sequence_version" in reference:
        result["sequence_version"] = reference["sequence_version"]
    if entry:
        if entry.get("seq") != seq or meta.get("release") != release:
            result["annotation_limitations"].append("residue_frame_sequence_or_release_mismatch")
        else:
            for feature in entry.get("ft", []):
                if (not isinstance(feature, list) or len(feature) < 3
                        or type(feature[0]) is not int or type(feature[1]) is not int
                        or not 1 <= feature[0] <= feature[1] <= len(seq)):
                    result["annotation_limitations"].append("invalid_residue_frame_feature")
                    continue
                result["generic_features"].append({
                    "start": feature[0], "end": feature[1], "trait_category": feature[2],
                    "source": "UniProt residue-frame", "source_release": meta["release"],
                    "evidence_role": "GENERIC_ANNOTATION_NOT_TRAIT_EVIDENCE",
                })
    result["annotation_limitations"] = sorted(set(result["annotation_limitations"]))
    return result


def load_discovery_entries(path: Path | None) -> dict:
    if path is None:
        return {}
    receipt = discovery_receipt(path)
    if receipt.get("entries_sha256") != digest(path):
        raise cm.CrossMechError("discovery entry bytes do not match the fetch receipt")
    document = json.loads(path.read_text())
    if (document.get("kind") != "cross-mech-uniprot-discovery-entries"
            or document.get("schema_version") != 1
            or document.get("uniprot_release") != receipt.get("expected_release")
            or any(document.get(key) != receipt.get(key) for key in
                   ("requested", "missing", "unavailable", "responses"))):
        raise cm.CrossMechError("invalid discovery entry envelope")
    requested, missing = receipt.get("requested"), receipt.get("missing")
    if (not isinstance(requested, list) or not isinstance(missing, list)
            or any(not isinstance(item, str) or not cm.PREFIXED_PROTEIN.fullmatch(item)
                   for item in requested + missing)
            or len(requested) != len(set(requested)) or len(missing) != len(set(missing))):
        raise cm.CrossMechError("invalid discovery accession sets")
    entries = {}
    for row in document["entries"]:
        seq = row["entry"].get("sequence", {}).get("value", "")
        if (row["protein_id"] in entries or not SEQUENCE_RE.fullmatch(seq)
                or row["protein_id"] != "UniProtKB:" + row["entry"].get("primaryAccession", "")
                or row["sequence_length"] != len(seq)
                or row["entry"]["sequence"].get("length") != len(seq)
                or row["sequence_sha256"] != hashlib.sha256(seq.encode("ascii")).hexdigest()
                or row["uniprot_release"] != document["uniprot_release"]):
            raise cm.CrossMechError("discovery protein identity/sequence/release mismatch")
        entries[row["protein_id"]] = row
    unavailable = receipt.get("unavailable", [])
    unavailable_ids = [row["protein_id"] for row in unavailable]
    if (set(entries) & set(missing) or set(entries) | set(missing) != set(requested)
            or receipt.get("discovered") != len(entries)
            or len(unavailable_ids) != len(set(unavailable_ids))
            or not set(unavailable_ids) <= set(missing)):
        raise cm.CrossMechError("discovery response does not close over its requested accessions")
    return entries


def discovery_receipt(path: Path | None) -> dict:
    if path is None:
        return {}
    if not path.name.endswith(".entries.json"):
        raise cm.CrossMechError("discovery input must end with .entries.json")
    receipt = json.loads(path.with_name(path.name.removesuffix(".entries.json") + ".receipt.json").read_text())
    if not RELEASE_RE.fullmatch(str(receipt.get("expected_release", ""))):
        raise cm.CrossMechError("discovery receipt lacks a valid release")
    return receipt


def discovery_resolution(protein: str, entries: dict, receipt: dict) -> dict:
    """Current lookup status is separate from a possibly historical sequence."""
    release = receipt.get("expected_release")
    if protein in entries:
        return {"status": "ACTIVE_EXACT_ACCESSION", "release": release}
    unavailable = [row for row in receipt.get("unavailable", []) if row["protein_id"] == protein]
    if len(unavailable) > 1:
        raise cm.CrossMechError(f"duplicate unavailable accession: {protein}")
    if unavailable:
        return {"status": unavailable[0]["reason"], "release": release,
                "inactive_reason": unavailable[0].get("inactive_reason")}
    return {"status": "NOT_RETURNED" if protein in receipt.get("missing", []) else "NOT_FETCHED",
            "release": release}


def discovery_candidates(path: Path | None, manifest: dict, proteins: set[str]) -> dict:
    """Display discovery separately; these rows never acquire qualified status."""
    by_protein = defaultdict(list)
    if path is None:
        return by_protein
    seen = set()
    for line in path.read_text().splitlines():
        row = json.loads(line)
        provenance = row.get("cross_mech_provenance", {})
        relative = row["record_path"]
        if (row["protein_id"] not in proteins or row["candidate_id"] in seen
                or row.get("qualification_status") != "CANDIDATE_PROTEIN"
                or provenance.get("snapshot_mentions_sha256") != manifest["mentions_sha256"]
                or not relative.startswith("data/traits/")
                or ".." in Path(relative).parts):
            raise cm.CrossMechError("candidate queue does not match the protein snapshot")
        seen.add(row["candidate_id"])
        by_protein[row["protein_id"]].append({
            "candidate_id": row["candidate_id"], "trait_id": row["trait_id"],
            "record_path": relative, "url": PTM_URL + quote(relative, safe="/"),
            "status": "DISCOVERY_CANDIDATE_NOT_CANONICAL", "mapping_method": row["mapping_method"],
            "scope": row["scope"], "source_release": row.get("source_release"),
            "trait_link_origin": provenance.get("trait_link_origin", "SIBLING_ASSERTION"),
        })
    return by_protein


def review_dispositions(prefixes: list[Path]) -> tuple[dict, dict]:
    """Project finalized decisions using their native digest/coverage verifier.

    Approval is not proof of installation. Retain history rather than silently
    overriding a rejection when two batches discuss the same pair.
    """
    from finalize_uniprot_review_batch import (
        _candidate_snapshot, _decision_partitions, _validate_record_groups,
    )
    by_protein = defaultdict(list)
    inputs = {}
    for prefix in sorted(set(prefixes)):
        resolved = Path(str(prefix) + ".resolved.jsonl")
        decisions_path = Path(str(prefix) + ".review-decisions.jsonl")
        candidates = _candidate_snapshot(resolved)
        decisions = _decision_partitions([decisions_path], candidates)
        _validate_record_groups(candidates, decisions)
        inputs.update({str(path): digest(path) for path in (resolved, decisions_path)})
        for candidate_id, decision in sorted(decisions.items()):
            row = candidates[candidate_id].row
            by_protein[row["protein_id"]].append({
                **decision.canonical_row(), "batch": str(prefix),
                "protein_id": row["protein_id"], "trait_id": row["trait_id"],
                "source_release": row["source_release"],
                "evidence_role": "REVIEW_DISPOSITION_NOT_INSTALLATION_PROOF",
            })
    return by_protein, inputs


def add_discovery_annotations(protein: str, payload: dict | None, entry: dict | None) -> dict | None:
    if entry is None:
        return payload
    if payload is None:
        payload = {key: entry[key] for key in ("protein_id", "sequence_length", "sequence_sha256", "uniprot_release")}
        payload.update(sequence=entry["entry"]["sequence"]["value"],
                       sequence_source="UniProt exact-entry discovery",
                       generic_features=[], annotation_limitations=[])
        version = entry["entry"].get("entryAudit", {}).get("sequenceVersion")
        if type(version) is int and version > 0:
            payload["sequence_version"] = version
    if (entry["sequence_sha256"] != payload["sequence_sha256"]
            or entry["uniprot_release"] != payload["uniprot_release"]):
        payload["annotation_limitations"].append("exact_entry_sequence_or_release_mismatch")
        return payload
    for feature in entry["entry"].get("features") or []:
        location = feature.get("location") or {}
        start, end = location.get("start", {}), location.get("end", {})
        first, last = start.get("value"), end.get("value")
        if (type(first) is not int or type(last) is not int
                or location.get("sequence") is not None
                or start.get("modifier", "EXACT") != "EXACT"
                or end.get("modifier", "EXACT") != "EXACT"
                or not 1 <= first <= last <= payload["sequence_length"]):
            payload["annotation_limitations"].append("uncertain_or_invalid_exact_entry_feature")
            continue
        payload["generic_features"].append({
            "start": first, "end": last, "source_feature": feature,
            "source": f"https://rest.uniprot.org/uniprotkb/{protein.split(':', 1)[1]}.json",
            "source_release": entry["uniprot_release"],
            "license": "CC-BY-4.0",
            "evidence_role": "GENERIC_ANNOTATION_NOT_TRAIT_EVIDENCE",
        })
    payload["annotation_limitations"] = sorted(set(payload["annotation_limitations"]))
    return payload


def build(snapshot: Path, traits: Path, registry: Path, frame_path: Path | None,
          discovery_path: Path | None = None, candidate_path: Path | None = None,
          review_prefixes: list[Path] | None = None) -> dict[str, str]:
    mentions, manifest = cm.load_snapshot(snapshot)
    by_protein = defaultdict(list)
    sources = {item["key"]: item for item in manifest["mechs"]}
    for mention in mentions:
        source = sources[mention["mech"]]
        by_protein[mention["protein_id"]].append({
            "mech": mention["mech"], "record_path": mention["record_path"],
            "pointer": mention["pointer"], "text_span": mention["text_span"],
            "role": mention["role"], "relation": mention["relation"],
            "annotations": mention["annotations"],
            "url": f"https://github.com/{source['github']}/blob/{source['commit']}/"
                   + quote(mention["record_path"], safe="/"),
        })
    sequences = ProteinSequenceRegistry(registry)
    references = {row["protein_id"]: row for row in
                  (json.loads(line) for line in registry.read_text().splitlines())}
    frame, meta = load_frame(frame_path)
    discovered = load_discovery_entries(discovery_path)
    receipt = discovery_receipt(discovery_path)
    candidates = discovery_candidates(candidate_path, manifest, set(by_protein))
    dispositions, review_inputs = review_dispositions(review_prefixes or [])
    examples = defaultdict(list)
    record_inputs = {}
    for path in matching_records(traits, set(by_protein)):
        record = yaml.load(path.read_text(), Loader=cm.Loader)  # noqa: S506
        if not isinstance(record, dict):
            raise cm.CrossMechError(f"{path}: record is not a mapping")
        relative = "data/traits/" + path.relative_to(traits).as_posix()
        for example in record.get("canonical_examples") or []:
            protein = example.get("protein_id")
            if protein not in by_protein:
                continue
            status = example.get("qualification_status") or "LEGACY_UNVERIFIED"
            item = {"trait_id": record["identifier"], "label": record.get("label"),
                    "record_path": relative, "url": PTM_URL + quote(relative, safe="/"),
                    "qualification_status": status, "trait_axis": record.get("trait_axis"),
                    "trait_category": record.get("trait_category"), "trait_occurrences": []}
            if status == "QUALIFIED":
                sequences.project(example, trait_id=record["identifier"], record_path=relative)
                item["trait_occurrences"] = example.get("trait_occurrences") or []
            examples[protein].append(item)
            record_inputs[relative] = digest(path)
    pair_report = cm.audit(mentions, traits_root=traits)
    pairs = defaultdict(list)
    for pair in pair_report["pairs"]:
        pairs[pair["protein_id"]].append(pair)
    proteins_out, sequences_out = [], []
    for protein in sorted(by_protein):
        ref = references.get(protein)
        payload = sequence_payload(protein, ref, frame, meta)
        payload = add_discovery_annotations(protein, payload, discovered.get(protein))
        if payload:
            sequences_out.append(payload)
        qualified = sum(item["qualification_status"] == "QUALIFIED" for item in examples[protein])
        qualified_traits = {item["trait_id"] for item in examples[protein]
                            if item["qualification_status"] == "QUALIFIED"}
        entry = discovered.get(protein, {}).get("entry", {})
        organism = entry.get("organism", {})
        description = entry.get("proteinDescription", {})
        protein_name = (description.get("recommendedName") or
                        next(iter(description.get("submissionNames", [])), {})).get("fullName", {}).get("value")
        proteins_out.append({
            "protein_id": protein,
            "url": "https://www.uniprot.org/uniprotkb/" + protein.split(":", 1)[1] + "/entry",
            "protein_label": ref.get("protein_label") if ref else protein_name,
            "taxon_id": ref.get("taxon_id") if ref else (
                f"NCBITaxon:{organism['taxonId']}" if organism.get("taxonId") else None),
            "taxon_label": ref.get("taxon_label") if ref else organism.get("scientificName"),
            "status": "HAS_QUALIFIED_PTM_EXAMPLE" if qualified else (
                "LEGACY_EXAMPLES_ONLY" if examples[protein] else "DISCOVERY_ONLY"),
            "sequence_status": payload["sequence_source"] if payload else "NOT_IN_AVAILABLE_INPUTS",
            "sequence_key": protein if payload else None,
            "current_uniprot_resolution": discovery_resolution(protein, discovered, receipt),
            "sibling_mentions": by_protein[protein],
            "sibling_trait_pairs": pairs[protein],
            "ptm_examples": sorted(examples[protein], key=lambda item: item["record_path"]),
            "discovery_candidates": sorted(
                [row for row in candidates[protein] if row["trait_id"] not in qualified_traits],
                key=lambda row: (row["trait_id"], row["candidate_id"])),
            "review_dispositions": dispositions[protein],
        })
    def encoded(rows):
        return "".join(cm.canonical_json(row) + "\n" for row in rows)
    inventory_text, sequence_text = encoded(proteins_out), encoded(sequences_out)
    summary = {
        "schema_version": 1, "kind": "proteintraitsmech-cross-mech-protein-inventory",
        "snapshot_manifest_sha256": digest(snapshot / cm.MANIFEST_NAME),
        "mentions_sha256": manifest["mentions_sha256"], "protein_registry_sha256": digest(registry),
        "residue_frame_sha256": digest(frame_path) if frame_path else None,
        "uniprot_discovery_sha256": digest(discovery_path) if discovery_path else None,
        "discovery_receipt_sha256": digest(discovery_path.with_name(
            discovery_path.name.removesuffix(".entries.json") + ".receipt.json")) if discovery_path else None,
        "candidate_queue_sha256": digest(candidate_path) if candidate_path else None,
        "review_input_sha256": review_inputs,
        "residue_frame_release": meta.get("release"), "record_sha256": record_inputs,
        "artifact_sha256": {"protein_inventory.jsonl": cm.sha256_text(inventory_text),
                            "protein_sequences.jsonl": cm.sha256_text(sequence_text)},
        "counts": {
            "mechs_scanned": len(sources), "proteins": len(proteins_out),
            "proteins_by_status": dict(sorted(Counter(row["status"] for row in proteins_out).items())),
            "sequences": len(sequences_out),
            "sequences_with_generic_annotations": sum(bool(row["generic_features"]) for row in sequences_out),
            "current_uniprot_resolution": dict(sorted(Counter(
                row["current_uniprot_resolution"]["status"] for row in proteins_out).items())),
            "discovery_pairs_not_installed": sum(len(row["discovery_candidates"]) for row in proteins_out),
            "proteins_with_discovery_candidates": sum(bool(row["discovery_candidates"]) for row in proteins_out),
            "review_decisions": dict(sorted(Counter(
                item["decision"] for row in proteins_out for item in row["review_dispositions"]).items())),
            "proteins_with_localized_qualified_traits": sum(any(
                occurrence["scope"] == "LOCALIZED" for example in row["ptm_examples"]
                for occurrence in example["trait_occurrences"]
            ) for row in proteins_out),
            "sibling_pair_statuses": pair_report["summary"]["pairs_by_status"],
        },
        "limitations": [
            "Inventory, not a new scientific qualification; existing QUALIFIED labels are projected.",
            "Only explicit UniProt identifiers in fleet-declared records are detected; gene names and other identifier namespaces require resolution.",
            "Text references and generic features do not assert a record-specific trait.",
            "Discovery candidates are a staging snapshot, not canonical examples; consult review dispositions before reconsidering known rejections.",
            "Trait record search includes hidden and ignored YAML files.",
            "Sequences absent from the supplied registry/frame remain visible, not guessed.",
        ],
    }
    lines = ["# Cross-Mech protein coverage", "", "Generated by `just build-cross-mech-inventory`. Do not edit.",
             "", "All detected accessions are listed, including discovery-only and legacy examples. "
             "Full links and trait occurrences: [protein_inventory.jsonl](protein_inventory.jsonl). "
             "Full sequences and generic tracks: [protein_sequences.jsonl](protein_sequences.jsonl). "
             "Input pins and limitations: [coverage.json](coverage.json).", "",
             "| Protein | Sibling Mechs | PTM qualified / legacy examples | Example traits (up to 3) | Discovery pairs | Sequence / current lookup |",
             "| --- | --- | ---: | --- | ---: | --- |"]
    for row in proteins_out:
        sibling_links = {}
        for mention in row["sibling_mentions"]:
            sibling_links.setdefault(mention["mech"], mention["url"])
        qualified = sum(item["qualification_status"] == "QUALIFIED" for item in row["ptm_examples"])
        links = ", ".join(f"[{key}]({url})" for key, url in sorted(sibling_links.items()))
        shown = sorted(row["ptm_examples"], key=lambda item: (
            item["qualification_status"] != "QUALIFIED", item["trait_id"]))[:3]
        example_links = ", ".join(
            f"[{item['trait_id']}]({item['url']})" +
            (" (legacy)" if item["qualification_status"] != "QUALIFIED" else "") for item in shown) or "—"
        lines.append(f"| [{row['protein_id']}]({row['url']}) | {links} | "
                     f"{qualified} / {len(row['ptm_examples']) - qualified} | "
                     f"{example_links} | {len(row['discovery_candidates'])} | {row['sequence_status']} / "
                     f"{row['current_uniprot_resolution']['status']} |")
    return dict(zip(OUTPUTS, (inventory_text, sequence_text,
                             json.dumps(summary, indent=2, sort_keys=True) + "\n",
                             "\n".join(lines) + "\n")))


def preserve_projection_inputs(out: Path, supplied: set[str], review_prefixes: list[Path]) -> None:
    """A cold/minimal build must not silently erase richer published coverage."""
    previous = out / "coverage.json"
    if not previous.is_file():
        return
    summary = json.loads(previous.read_text())
    missing = [key for key in ("residue_frame_sha256", "uniprot_discovery_sha256", "candidate_queue_sha256")
               if summary.get(key) and key not in supplied]
    review_paths = {str(prefix) + suffix for prefix in review_prefixes
                    for suffix in (".resolved.jsonl", ".review-decisions.jsonl")}
    if set(summary.get("review_input_sha256", {})) - review_paths:
        missing.append("previous review batches")
    if missing:
        raise cm.CrossMechError("refusing to discard published projection inputs: " + ", ".join(missing)
                               + "; supply the same input lanes or choose a new --out directory")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, default=cm.SNAPSHOT_DIR)
    parser.add_argument("--traits", type=Path, default=cm.TRAITS_ROOT)
    parser.add_argument("--registry", type=Path, default=ROOT / "data/grounding/protein_registry.jsonl")
    parser.add_argument("--residue-frame", type=Path)
    parser.add_argument("--uniprot-discovery", type=Path, help="receipt-bound discovery.entries.json")
    parser.add_argument("--candidate-queue", type=Path, help="cross-Mech candidate JSONL for discovery links, not installation proof")
    parser.add_argument("--review-batch", type=Path, action="append", default=[],
                        help="resolved + finalized review-decisions filename prefix; repeat for history")
    parser.add_argument("--out", type=Path, default=cm.SNAPSHOT_DIR)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if args.apply or args.check:
        supplied = {key for key, value in (("residue_frame_sha256", args.residue_frame),
                    ("uniprot_discovery_sha256", args.uniprot_discovery),
                    ("candidate_queue_sha256", args.candidate_queue)) if value is not None}
        preserve_projection_inputs(args.out, supplied, args.review_batch)
    outputs = build(args.snapshot, args.traits, args.registry, args.residue_frame,
                    args.uniprot_discovery, args.candidate_queue, args.review_batch)
    print(json.dumps(json.loads(outputs["coverage.json"])["counts"], indent=2, sort_keys=True))
    if args.check:
        stale = [name for name, text in outputs.items()
                 if not (args.out / name).is_file() or (args.out / name).read_text() != text]
        if stale:
            raise cm.CrossMechError(f"inventory differs from current inputs: {', '.join(stale)}")
    elif args.apply:
        for name, text in outputs.items():
            cm._atomic_write(args.out / name, text)
    else:
        print("Dry run; use --apply to publish the derived inventory (no trait writes).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
