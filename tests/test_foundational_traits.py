"""Tests for foundational protein trait records and the add-record workflow."""

from __future__ import annotations

import pathlib
import sys
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import build_docs_index as bdi  # noqa: E402
import seed_foundational_traits as sft  # noqa: E402
import validate_strict as vs  # noqa: E402


def test_foundational_trait_records_exist_and_validate():
    """Every record defined in seed_foundational_traits must exist on disk and pass strict validation."""
    assert len(sft.SPECS) == 66
    seen_ids: set[str] = set()
    for spec in sft.SPECS:
        assert spec.identifier not in seen_ids, f"duplicate identifier: {spec.identifier}"
        seen_ids.add(spec.identifier)
        path = sft.TRAITS_DIR / spec.rel_dir / spec.filename
        assert path.is_file(), f"missing record file: {path}"
        errors = vs.validate_one(path)
        assert not errors, f"validation errors in {path}: {errors}"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert data["identifier"] == spec.identifier
        assert data["label"] == spec.label
        assert data["trait_axis"] == spec.trait_axis
        assert data["trait_category"] == spec.trait_category
        assert data["term_kind"] == "CLASS"
        methods = data.get("detection_methods") or []
        assert methods, f"{spec.identifier} must include at least one runnable detection_method"
        for m in methods:
            assert m.get("recipe"), f"{spec.identifier} detection_method missing recipe"
            assert str(m.get("edam_operation", "")).startswith("EDAM:operation_")
            assert str(m.get("evidence_code", "")).startswith("ECO:")
            assert str(m.get("reference", "")).startswith(("DOI:", "PMID:"))
        if spec.identifier.startswith("proteintraitsmech:"):
            assert bdi.infer_source(spec.identifier, path) == "curated"
        elif spec.identifier.startswith("GO:"):
            assert bdi.infer_source(spec.identifier, path) == "manual"


def test_cross_mech_obsolete_go_xref_merged():
    """GO:0004085 (obsolete butyryl-CoA dehydrogenase activity) is merged onto GO:0016937."""
    target = (
        sft.TRAITS_DIR
        / "function/molecular_function/go/short-chain-fatty-acyl-coa-dehydrogenase-activity-go0016937.yaml"
    )
    assert target.is_file()
    errors = vs.validate_one(target)
    assert not errors, f"validation errors in {target}: {errors}"
    data = yaml.safe_load(target.read_text(encoding="utf-8"))
    assert "GO:0004085" in (data.get("xrefs") or [])
    path, seed_text = sft.go_0016937_seed()
    assert path == target
    assert seed_text is not None and "GO:0004085" in seed_text


def test_disulfide_infer_source_distinguishes_lsf_parent_from_curated_subtypes():
    """DISULFIDE_BOND stays LinkML LSF while DISULFIDE_* subtypes resolve to curated."""
    dummy = ROOT / "data/traits/structure/disulfide/x.yaml"
    assert bdi.infer_source("proteintraitsmech:DISULFIDE_BOND", dummy) == "LinkML LSF"
    assert bdi.infer_source("proteintraitsmech:DISULFIDE_INTRACHAIN", dummy) == "curated"
    assert bdi.infer_source("proteintraitsmech:DISULFIDE_FUTURE_SUBTYPE", dummy) == "curated"


def test_previously_empty_class_categories_are_populated():
    """All 7 previously empty class-level categories now have populated directories."""
    expected_dirs = {
        "SEQ_NONSTANDARD_RESIDUE": (sft.TRAITS_DIR / "sequence/nonstandard_residue", 4),
        "SEQ_LOW_COMPLEXITY": (sft.TRAITS_DIR / "sequence/low_complexity", 4),
        "SEQ_COMPOSITION": (sft.TRAITS_DIR / "sequence/composition", 10),
        "STRUCT_QUATERNARY": (sft.TRAITS_DIR / "structure/quaternary", 11),
        "STRUCT_ALLOSTERIC_SITE": (sft.TRAITS_DIR / "structure/allosteric_site", 5),
        "STRUCT_SYMMETRY": (sft.TRAITS_DIR / "structure/symmetry", 9),
        "MIXED_COILED_COIL": (sft.TRAITS_DIR / "sequence_structure/coiled_coil", 7),
    }
    for cat, (d, min_count) in expected_dirs.items():
        files = list(d.glob("*.yaml"))
        assert len(files) >= min_count, f"{cat} expected >= {min_count} records in {d}, found {len(files)}"
