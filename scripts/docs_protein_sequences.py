"""Read-only projection of qualified examples' authoritative full sequences.

This does not qualify examples, replay occurrence evidence, fetch annotations,
or infer trait positions. Those remain the grounding pipeline's responsibilities.
It reuses the grounding validator's reference and snapshot checks so the browser
never attaches a different release, organism, or isoform sequence to an example.
"""

from __future__ import annotations

from pathlib import Path

from validate_uniprot_grounding import _validate_qualified_example, load_registry


class ProteinSequenceRegistry:
    """A once-loaded, validated ProteinReference registry for one docs build."""

    def __init__(self, path: Path):
        self._references, findings = load_registry(path)
        if findings:
            details = "; ".join(f"{f.file}: {f.code}: {f.message}" for f in findings[:3])
            raise ValueError(f"invalid protein sequence registry ({len(findings)} findings): {details}")

    def project(self, example: dict, *, trait_id: str = "", record_path: str = "<memory>") -> dict:
        """Return sequence/provenance only; never upgrade a legacy example."""
        if example.get("qualification_status") != "QUALIFIED":
            return {}
        reference = self._references.get(example.get("protein_id"))
        findings = _validate_qualified_example(
            example, record={"identifier": trait_id}, reference=reference,
            file=record_path, example_index=0,
        )
        if findings:
            details = "; ".join(f"{f.code}: {f.message}" for f in findings[:3])
            raise ValueError(f"{record_path}: {example.get('protein_id')}: sequence binding: {details}")
        # The validator above rejects a missing exact reference and any stale
        # inline sequence. Do not graft a legacy feature track onto a newly
        # hydrated sequence without its original matching inline frame.
        assert reference is not None
        features = example.get("features") or []
        if features and not example.get("sequence"):
            raise ValueError(f"{record_path}: {example['protein_id']}: feature track has no inline sequence")
        for feature in features:
            start, end = feature.get("start"), feature.get("end")
            if (type(start) is not int or type(end) is not int
                    or not 1 <= start <= end <= reference["sequence_length"]):
                raise ValueError(f"{record_path}: {example['protein_id']}: invalid generic feature bounds")
        result = {
            "seq": reference["sequence"], "seqsrc": "ProteinReference",
            "seqsha": reference["sequence_sha256"], "rel": reference["uniprot_release"],
        }
        if "sequence_version" in reference:
            result["sv"] = reference["sequence_version"]
        return result
