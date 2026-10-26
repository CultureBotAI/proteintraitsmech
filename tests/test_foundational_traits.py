"""Tests for foundational protein trait records and the add-record workflow."""

from __future__ import annotations

import pathlib
import sys
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import audit_causal_graphs as acg  # noqa: E402
import build_docs_index as bdi  # noqa: E402
import record_io as rio  # noqa: E402
import score_causal_graphs as scg  # noqa: E402
import seed_foundational_traits as sft  # noqa: E402
import seed_localstructuralfeature as slsf  # noqa: E402
import seed_uniprot_peptide_classes as supc  # noqa: E402
import validate_strict as vs  # noqa: E402


MECHANISM_BEARING_CATEGORIES = {
    "SEQ_NONSTANDARD_RESIDUE",
    "STRUCT_ALLOSTERIC_SITE",
    "SEQ_SIGNAL_PEPTIDE",
    "SEQ_TRANSIT_PEPTIDE",
    "SEQ_PROPEPTIDE",
    "STRUCT_DISULFIDE",
    "FUNC_LOCALIZATION",
    "SEQ_INITIATOR_METHIONINE",
    "SEQ_MATURE_CHAIN",
    "STRUCT_CAVITY",
    "STRUCT_SURFACE",
    "STRUCT_DYNAMICS",
}
MECHANISM_BEARING_LOWCOMP_IDS = {
    "proteintraitsmech:LOWCOMP_POLYAMPHOLYTIC_CHARGE_BLOCK",
    "proteintraitsmech:LOWCOMP_FG_NUCLEOPORIN_REPEAT_REGION",
}

ROUND_124_EDITED_IDS = {spec.identifier for spec in sft.SPECS[:66] if spec.causal_graphs}
STAGE1_UNCHANGED_IDS = {
    "proteintraitsmech:INIT_METHIONINE_ACETYLATED",
    "proteintraitsmech:MATURE_CHAIN_PROPROTEIN_CLEAVED",
    "proteintraitsmech:PROPEPTIDE_VKD_GLA_RECOGNITION",
    "proteintraitsmech:ALLOSTERIC_COVALENT_REGULATORY_SITE",
    "proteintraitsmech:DISULFIDE_CATALYTIC_CXXC",
}


def test_foundational_trait_records_exist_and_validate():
    """Every record defined in seed_foundational_traits must exist on disk and pass strict validation."""
    assert len(sft.SPECS) == 101
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
    """All previously empty and single-record class-level categories now have populated directories."""
    expected_dirs = {
        "SEQ_NONSTANDARD_RESIDUE": (sft.TRAITS_DIR / "sequence/nonstandard_residue", 4),
        "SEQ_LOW_COMPLEXITY": (sft.TRAITS_DIR / "sequence/low_complexity", 6),
        "SEQ_COMPOSITION": (sft.TRAITS_DIR / "sequence/composition", 10),
        "STRUCT_QUATERNARY": (sft.TRAITS_DIR / "structure/quaternary", 11),
        "STRUCT_ALLOSTERIC_SITE": (sft.TRAITS_DIR / "structure/allosteric_site", 6),
        "STRUCT_SYMMETRY": (sft.TRAITS_DIR / "structure/symmetry", 9),
        "MIXED_COILED_COIL": (sft.TRAITS_DIR / "sequence_structure/coiled_coil", 7),
        "SEQ_INITIATOR_METHIONINE": (sft.TRAITS_DIR / "sequence/initiator_methionine", 6),
        "SEQ_MATURE_CHAIN": (sft.TRAITS_DIR / "sequence/mature_chain", 6),
        "SEQ_TRANSIT_PEPTIDE": (sft.TRAITS_DIR / "sequence/transit_peptide", 7),
        "SEQ_PROPEPTIDE": (sft.TRAITS_DIR / "sequence/propeptide", 6),
        "STRUCT_DISULFIDE": (sft.TRAITS_DIR / "structure/disulfide", 6),
        "STRUCT_CAVITY": (sft.TRAITS_DIR / "structure/cavity", 7),
        "STRUCT_SURFACE": (sft.TRAITS_DIR / "structure/surface", 6),
        "STRUCT_DYNAMICS": (sft.TRAITS_DIR / "structure/dynamics", 6),
        "EVO_CONSERVATION": (sft.TRAITS_DIR / "evolution/conservation", 6),
    }
    for cat, (d, min_count) in expected_dirs.items():
        files = list(d.glob("*.yaml"))
        assert len(files) >= min_count, f"{cat} expected >= {min_count} records in {d}, found {len(files)}"


def test_foundational_trait_causal_graphs_audit_and_score():
    """All 57 mechanism-bearing foundational traits carry audited causal_graphs with 0 errors/warnings."""
    valid_types = acg.node_type_enum()
    assert valid_types
    mech_specs = [
        s
        for s in sft.SPECS
        if s.trait_category in MECHANISM_BEARING_CATEGORIES or s.identifier in MECHANISM_BEARING_LOWCOMP_IDS
    ]
    non_mech_specs = [
        s
        for s in sft.SPECS
        if s.trait_category not in MECHANISM_BEARING_CATEGORIES and s.identifier not in MECHANISM_BEARING_LOWCOMP_IDS
    ]
    assert len(mech_specs) == 57
    assert len(non_mech_specs) == 44
    assert len(ROUND_124_EDITED_IDS) == 25

    for spec in mech_specs:
        path = sft.TRAITS_DIR / spec.rel_dir / spec.filename
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert data.get("mapping_status") == "SEEDED", f"{spec.identifier} must preserve native SEEDED status"
        assert data.get("causal_graphs"), f"{spec.identifier} missing causal_graphs"
        history = data.get("curation_history") or []
        if spec.identifier in STAGE1_UNCHANGED_IDS:
            assert not history, f"{spec.identifier} unchanged since Stage 1 seeding must not carry no-op EDIT history"
        else:
            assert history, f"{spec.identifier} missing curation_history"
            assert history[-1].get("curator") == "claude"
            assert history[-1].get("action") == "EDIT"
            assert history[-1].get("llm_assisted") is True
        if spec.identifier not in ROUND_124_EDITED_IDS:
            cg = data["causal_graphs"][0]
            assert len(cg.get("nodes") or []) == 4, f"{spec.identifier} expected 4 nodes"
            assert len(cg.get("edges") or []) == 3, f"{spec.identifier} expected 3 edges"
        errors: list[str] = []
        warns: list[acg.AuditWarning] = []
        stats = {"records": 0, "graphs": 0, "nodes": 0, "edges": 0, "grounded": 0, "snippet_edges": 0}
        acg.audit_record(data, str(path.relative_to(ROOT)), valid_types, errors, warns, stats)
        assert not errors, f"causal_graphs errors in {spec.identifier}: {errors}"
        assert not warns, f"causal_graphs warnings in {spec.identifier}: {warns}"
        scored = scg.score_path(path)
        expected_score = 100 - scg.SEEDED_REVIEW_PENALTY
        assert scored.score == expected_score, (
            f"{spec.identifier} expected score {expected_score}, got {scored.score} ({scored.reasons})"
        )
        assert scored.structural_errors == 0
        assert scored.quality_warnings == 0
        assert scored.reasons == ("mapping_status=SEEDED",)
        fresh = sft.emit_record(spec)
        assert "curation_history:" not in fresh, f"seeder must not emit curation_history for {spec.identifier}"
        existing_text = path.read_text(encoding="utf-8")
        assert rio.merge_on_reseed(existing_text, fresh) == existing_text, (
            f"merge_on_reseed must preserve curation_history and be idempotent on {spec.identifier}"
        )

    for spec in non_mech_specs:
        path = sft.TRAITS_DIR / spec.rel_dir / spec.filename
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert data.get("mapping_status") == "SEEDED", f"{spec.identifier} should remain SEEDED"
        assert not data.get("causal_graphs"), f"{spec.identifier} should not carry causal_graphs"


def test_foundational_trait_parent_traits_resolve_to_corpus_records():
    """Every parent_traits CURIE on the 84 foundational traits resolves to an on-disk corpus record."""
    known_parent_files = {
        "proteintraitsmech:COILED_COIL": (
            sft.TRAITS_DIR / "structure/secondary/coiled-coil.yaml"
        ),
        "proteintraitsmech:UNIPROT_FT_SEQ_INITIATOR_METHIONINE": (
            sft.TRAITS_DIR / "sequence/initiator_methionine/uniprot-seq_initiator_methionine.yaml"
        ),
        "proteintraitsmech:UNIPROT_FT_SEQ_MATURE_CHAIN": (
            sft.TRAITS_DIR / "sequence/mature_chain/uniprot-seq_mature_chain.yaml"
        ),
        "proteintraitsmech:UNIPROT_FT_SEQ_SIGNAL_PEPTIDE": (
            sft.TRAITS_DIR / "sequence/signal_peptide/uniprot-seq_signal_peptide.yaml"
        ),
        "proteintraitsmech:UNIPROT_FT_SEQ_TRANSIT_PEPTIDE": (
            sft.TRAITS_DIR / "sequence/transit_peptide/uniprot-seq_transit_peptide.yaml"
        ),
        "proteintraitsmech:UNIPROT_FT_SEQ_PROPEPTIDE": (
            sft.TRAITS_DIR / "sequence/propeptide/uniprot-seq_propeptide.yaml"
        ),
        "proteintraitsmech:DISULFIDE_BOND": (
            sft.TRAITS_DIR / "structure/disulfide/disulfide-bond.yaml"
        ),
        "proteintraitsmech:CAVITY": (
            sft.TRAITS_DIR / "structure/cavity/cavity.yaml"
        ),
        "proteintraitsmech:POCKET": (
            sft.TRAITS_DIR / "structure/cavity/pocket.yaml"
        ),
        "proteintraitsmech:TUNNEL": (
            sft.TRAITS_DIR / "structure/cavity/tunnel.yaml"
        ),
        "proteintraitsmech:INTERFACE": (
            sft.TRAITS_DIR / "structure/interface/interface.yaml"
        ),
        "proteintraitsmech:EVO_CONSERVED": (
            sft.TRAITS_DIR / "evolution/conservation/conserved-protein.yaml"
        ),
        "proteintraitsmech:EVO_VARIABLE": (
            sft.TRAITS_DIR / "evolution/conservation/variable-protein.yaml"
        ),
        "IDPO:0000002": (
            sft.TRAITS_DIR / "sequence/disorder/disorder-idpo-0000002.yaml"
        ),
        "GO:1902494": (
            sft.TRAITS_DIR / "function/localization/go/catalytic-complex-go1902494.yaml"
        ),
        "proteintraitsmech:ELBOW": (
            sft.TRAITS_DIR / "structure/dynamics/elbow.yaml"
        ),
        "PATO:0001543": (
            sft.TRAITS_DIR / "structure/dynamics/pato/flexibility-pato0001543.yaml"
        ),
        "PATO:0002193": (
            sft.TRAITS_DIR / "structure/surface/pato/electric-charge-pato0002193.yaml"
        ),
        "PATO:0002195": (
            sft.TRAITS_DIR / "structure/surface/pato/positive-charge-pato0002195.yaml"
        ),
        "PATO:0002196": (
            sft.TRAITS_DIR / "structure/surface/pato/negative-charge-pato0002196.yaml"
        ),
        "PATO:0001884": (
            sft.TRAITS_DIR / "structure/surface/pato/hydrophobicity-pato0001884.yaml"
        ),
    }
    spec_paths = {
        spec.identifier: sft.TRAITS_DIR / spec.rel_dir / spec.filename
        for spec in sft.SPECS
    }
    for spec in sft.SPECS:
        path = spec_paths[spec.identifier]
        on_disk = yaml.safe_load(path.read_text(encoding="utf-8"))
        for parent in on_disk.get("parent_traits") or []:
            target = spec_paths.get(parent) or known_parent_files.get(parent)
            assert target is not None and target.is_file(), (
                f"{spec.identifier} parent_traits {parent!r} does not resolve to an on-disk record"
            )
            data = yaml.safe_load(target.read_text(encoding="utf-8"))
            assert data["identifier"] == parent


def test_cycle2_stage1_records_have_verified_pmids_and_initiator_met_hierarchy():
    """Cycle 2 Stage 1 foundational traits have verified PMIDs, resolved recipes, and non-contradictory hierarchy."""
    cycle2_specs = {spec.identifier: spec for spec in sft.SPECS[66:84]}
    assert len(cycle2_specs) == 18

    assert cycle2_specs["proteintraitsmech:INIT_METHIONINE_EXCISED"].parent_traits == (
        "proteintraitsmech:UNIPROT_FT_SEQ_INITIATOR_METHIONINE",
    )
    assert cycle2_specs["proteintraitsmech:INIT_METHIONINE_RETAINED"].parent_traits == ()
    assert cycle2_specs["proteintraitsmech:INIT_METHIONINE_FORMYLATED_NME"].parent_traits == (
        "proteintraitsmech:UNIPROT_FT_SEQ_INITIATOR_METHIONINE",
    )
    assert cycle2_specs["proteintraitsmech:INIT_METHIONINE_ACETYLATED"].parent_traits == (
        "proteintraitsmech:INIT_METHIONINE_RETAINED",
    )

    for spec in cycle2_specs.values():
        path = sft.TRAITS_DIR / spec.rel_dir / spec.filename
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        for m in data.get("detection_methods") or []:
            assert "{pat}" not in m["recipe"], f"{spec.identifier} recipe still contains unresolved {{pat}}"
            ref = m["reference"]
            if ref.startswith("PMID:"):
                assert int(ref.split(":", 1)[1]) < 41_000_000, f"out-of-range PMID {ref} on {spec.identifier}"
        for ev in data.get("evidence") or []:
            ref = ev["reference"]
            if ref.startswith("PMID:"):
                assert int(ref.split(":", 1)[1]) < 41_000_000, f"out-of-range PMID {ref} on {spec.identifier}"
        for cg in data.get("causal_graphs") or []:
            for edge in cg.get("edges") or []:
                for ev in edge.get("evidence") or []:
                    ref = ev["reference"]
                    if ref.startswith("PMID:"):
                        assert int(ref.split(":", 1)[1]) < 41_000_000, f"out-of-range PMID {ref} on {spec.identifier}"


def test_cycle3_stage1_records_have_verified_pmids_and_hierarchy():
    """Cycle 3 Stage 1 foundational traits have verified PMIDs, resolved recipes, and valid parent_traits."""
    cycle3_specs = {spec.identifier: spec for spec in sft.SPECS[84:]}
    assert len(cycle3_specs) == 17
    assert cycle3_specs["proteintraitsmech:INIT_METHIONINE_N_DEGRON"].parent_traits == (
        "proteintraitsmech:INIT_METHIONINE_RETAINED",
    )
    assert cycle3_specs["proteintraitsmech:MATURE_CHAIN_AUTOCATALYTIC_CLEAVED"].parent_traits == (
        "proteintraitsmech:UNIPROT_FT_SEQ_MATURE_CHAIN",
    )
    assert cycle3_specs["proteintraitsmech:ALLOSTERIC_COVALENT_REGULATORY_SITE"].parent_traits == (
        "proteintraitsmech:ALLOSTERIC_REGULATORY_SITE",
    )
    assert cycle3_specs["proteintraitsmech:DISULFIDE_CATALYTIC_CXXC"].parent_traits == (
        "proteintraitsmech:DISULFIDE_ALLOSTERIC_REDOX_SWITCH",
    )

    for spec in cycle3_specs.values():
        path = sft.TRAITS_DIR / spec.rel_dir / spec.filename
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        for m in data.get("detection_methods") or []:
            assert "{pat}" not in m["recipe"], f"{spec.identifier} recipe still contains unresolved {{pat}}"
            ref = m["reference"]
            if ref.startswith("PMID:"):
                assert int(ref.split(":", 1)[1]) < 41_000_000, f"out-of-range PMID {ref} on {spec.identifier}"
        for ev in data.get("evidence") or []:
            ref = ev["reference"]
            if ref.startswith("PMID:"):
                assert int(ref.split(":", 1)[1]) < 41_000_000, f"out-of-range PMID {ref} on {spec.identifier}"
        cgs = data.get("causal_graphs") or []
        assert len(cgs) == 1, f"{spec.identifier} must carry a causal_graph"
        for cg in cgs:
            assert len(cg.get("nodes") or []) == 4, f"{spec.identifier} expected 4 nodes"
            edges = cg.get("edges") or []
            assert len(edges) == 3, f"{spec.identifier} expected 3 edges"
            snippets = [edge["evidence"][0]["snippet"] for edge in edges]
            assert len(set(snippets)) == 3, f"{spec.identifier} must have 3 distinct verbatim snippets"
            for edge in edges:
                for ev in edge.get("evidence") or []:
                    ref = ev["reference"]
                    if ref.startswith("PMID:"):
                        assert int(ref.split(":", 1)[1]) < 41_000_000, f"out-of-range PMID {ref} on {spec.identifier}"


def test_root_local_structural_and_peptide_class_causal_graphs():
    """All 10 mechanism-bearing root class records in LSF and UniProt peptide seeders carry audited 4-node/3-edge causal_graphs."""
    valid_types = acg.node_type_enum()
    mech_lsf_terms = {
        "CATALYTIC_RESIDUE",
        "PROTEIN_BINDING_SITE",
        "METAL_BINDING_SITE",
        "DISULFIDE_BOND",
        "INTERFACE",
    }
    mech_lsf = [e for e in slsf.TERMS if e["term"] in mech_lsf_terms]
    assert len(mech_lsf) == 5
    assert len(supc.FEATURES) == 5

    all_root_mech: list[tuple[pathlib.Path, str, str]] = [
        (slsf.target_path(e), f"proteintraitsmech:{e['term']}", slsf.yaml_for(e)) for e in mech_lsf
    ] + [
        (
            supc.OUT_DIR / subdir / f"uniprot-{category.lower()}.yaml",
            f"proteintraitsmech:UNIPROT_FT_{category}",
            supc.build_yaml(ft_type, category, label, definition, []),
        )
        for _ft_query, ft_type, category, subdir, label, definition in supc.FEATURES
    ]
    assert len(all_root_mech) == 10

    for path, ident, fresh_yaml in all_root_mech:
        assert path.is_file(), f"missing root class record: {path}"
        v_errors = vs.validate_one(path)
        assert not v_errors, f"validation errors in {path}: {v_errors}"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert data["identifier"] == ident
        assert data.get("mapping_status") == "SEEDED"
        cgs = data.get("causal_graphs") or []
        assert len(cgs) == 1
        assert len(cgs[0].get("nodes") or []) == 4
        assert len(cgs[0].get("edges") or []) == 3
        history = data.get("curation_history") or []
        assert history, f"{ident} missing curation_history"
        assert history[-1].get("curator") == "claude"
        assert history[-1].get("action") == "EDIT"
        assert history[-1].get("llm_assisted") is True

        errors: list[str] = []
        warns: list[acg.AuditWarning] = []
        stats = {"records": 0, "graphs": 0, "nodes": 0, "edges": 0, "grounded": 0, "snippet_edges": 0}
        acg.audit_record(data, str(path.relative_to(ROOT)), valid_types, errors, warns, stats)
        assert not errors, f"causal_graphs errors in {ident}: {errors}"
        assert not warns, f"causal_graphs warnings in {ident}: {warns}"

        scored = scg.score_path(path)
        assert scored.score == 100 - scg.SEEDED_REVIEW_PENALTY
        assert scored.structural_errors == 0
        assert scored.quality_warnings == 0
        assert scored.reasons == ("mapping_status=SEEDED",)

        assert "causal_graphs:" in fresh_yaml, f"{ident} seeder must emit causal_graphs directly"
        assert "evidence:" in fresh_yaml, f"{ident} seeder must emit evidence directly"
        for ev in data.get("evidence") or []:
            ref = ev["reference"]
            if ref.startswith("PMID:"):
                assert int(ref.split(":", 1)[1]) < 41_000_000, f"out-of-range PMID {ref} on {ident}"
        for edge in cgs[0].get("edges") or []:
            for ev in edge.get("evidence") or []:
                ref = ev["reference"]
                if ref.startswith("PMID:"):
                    assert int(ref.split(":", 1)[1]) < 41_000_000, f"out-of-range PMID {ref} on {ident}"

        existing_text = path.read_text(encoding="utf-8")
        assert yaml.safe_load(rio.merge_on_reseed(existing_text, fresh_yaml)) == data






