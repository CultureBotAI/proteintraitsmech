#!/usr/bin/env python3
"""Seed foundational class-level protein traits across empty and sparse categories.

Fills the 7 zero-record domain categories in ProteinTraitCategoryEnum:
  - SEQ_NONSTANDARD_RESIDUE (data/traits/sequence/nonstandard_residue/)
  - SEQ_LOW_COMPLEXITY      (data/traits/sequence/low_complexity/)
  - SEQ_COMPOSITION         (data/traits/sequence/composition/)
  - STRUCT_QUATERNARY       (data/traits/structure/quaternary/)
  - STRUCT_ALLOSTERIC_SITE  (data/traits/structure/allosteric_site/)
  - STRUCT_SYMMETRY         (data/traits/structure/symmetry/)
  - MIXED_COILED_COIL       (data/traits/sequence_structure/coiled_coil/)

Expands the 4 single-record categories where canonical subclasses were absent:
  - SEQ_SIGNAL_PEPTIDE      (data/traits/sequence/signal_peptide/)
  - SEQ_TRANSIT_PEPTIDE     (data/traits/sequence/transit_peptide/)
  - SEQ_PROPEPTIDE          (data/traits/sequence/propeptide/)
  - STRUCT_DISULFIDE        (data/traits/structure/disulfide/)

And resolves the cross-Mech GO gaps:
  - GO:7770085 (protocatechuate 3,4-dioxygenase complex, FUNC_LOCALIZATION)
  - GO:0004085 (merged alt_id on GO:0016937 short-chain fatty acyl-CoA dehydrogenase activity)

Every record is routed through `record_io.write_record(..., validate=True)`.
Idempotent; dry-run by default (`--apply` to write, `--force` to re-merge existing).
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from record_io import write_record  # noqa: E402
from yaml_emit import folded, yaml_escape  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
TRAITS_DIR = REPO_ROOT / "data" / "traits"
DEF_SOURCE = "ProteinTraitsMech curated protein-trait taxonomy"
LICENSE = "CC-BY-4.0"


@dataclass(frozen=True)
class MethodSpec:
    name: str
    method_type: str
    edam_operation: str
    tool: str
    evidence_code: str
    reference: str
    recipe: str


@dataclass(frozen=True)
class TraitSpec:
    rel_dir: str
    filename: str
    identifier: str
    label: str
    definition: str
    trait_axis: str
    trait_category: str
    parent_traits: tuple[str, ...] = ()
    synonyms: tuple[tuple[str, str], ...] = ()
    xrefs: tuple[str, ...] = ()
    sequence_pattern: str | None = None
    evidence: tuple[tuple[str, str], ...] = ()
    detection_methods: tuple[MethodSpec, ...] = ()
    definition_source: str = DEF_SOURCE


M_SECIS = MethodSpec(
    name="SecMarker / Infernal SECIS + TGA selenoprotein prediction",
    method_type="HMM_PROFILE",
    edam_operation="EDAM:operation_0415",
    tool="https://secmarker.crg.es/",
    evidence_code="ECO:0000255",
    reference="PMID:24070661",
    recipe="cmsearch --cpu 4 --tblout {output} RF00031.cm {input}",
)
M_PYL = MethodSpec(
    name="HMMER PylRS/tRNA(Pyl) & in-frame UAG pyrrolysine detection",
    method_type="HMM_PROFILE",
    edam_operation="EDAM:operation_0300",
    tool="biotools:hmmer3",
    evidence_code="ECO:0000259",
    reference="PMID:21926992",
    recipe="hmmsearch --cut_ga --domtblout {output} PylB_PylC_PylD.hmm {input}",
)
M_FMET = MethodSpec(
    name="N-terminal initiator fMet / deformylase motif scan",
    method_type="SEQUENCE_PATTERN",
    edam_operation="EDAM:operation_0239",
    tool="biotools:emboss",
    evidence_code="ECO:0000255",
    reference="PMID:16336047",
    recipe="fuzzpro -sequence {input} -pattern '^M[ACDEFGHIKLMNPQRSTVWY]' -outfile {output}",
)
M_DAMINO = MethodSpec(
    name="Radical-SAM epimerase / post-translational D-residue HMM scan",
    method_type="HMM_PROFILE",
    edam_operation="EDAM:operation_0300",
    tool="biotools:hmmer3",
    evidence_code="ECO:0000259",
    reference="PMID:23064350",
    recipe="hmmsearch --cut_ga --domtblout {output} PoyD_YydG_epimerase.hmm {input}",
)
M_SEG = MethodSpec(
    name="SEG / fLPS low-complexity sequence segmentation",
    method_type="SEQUENCE_PATTERN",
    edam_operation="EDAM:operation_0234",
    tool="biotools:flps",
    evidence_code="ECO:0000362",
    reference="PMID:28851299",
    recipe="fLPS -t 1e-5 {input} > {output}",
)
M_PLAAC = MethodSpec(
    name="PLAAC HMM prion-like amino-acid composition scan",
    method_type="HMM_PROFILE",
    edam_operation="EDAM:operation_0234",
    tool="biotools:plaac",
    evidence_code="ECO:0000362",
    reference="PMID:24667259",
    recipe="java -jar plaac.jar -i {input} -p all > {output}",
)
M_FLPS = MethodSpec(
    name="fLPS2 compositional bias binomial P-value scan",
    method_type="SEQUENCE_PATTERN",
    edam_operation="EDAM:operation_0234",
    tool="biotools:flps",
    evidence_code="ECO:0007669",
    reference="PMID:28851299",
    recipe="fLPS -t 1e-5 -c default {input} > {output}",
)
M_PISA = MethodSpec(
    name="PDBePISA macromolecular interface & quaternary assembly analysis",
    method_type="STRUCTURAL_ALGORITHM",
    edam_operation="EDAM:operation_0248",
    tool="biotools:pdbepisa",
    evidence_code="ECO:0007669",
    reference="PMID:17681537",
    recipe="pisa {id} -analyse {input} && pisa {id} -xml assemblies > {output}",
)
M_FPOCKET = MethodSpec(
    name="Fpocket / AlloSitePro allosteric & cryptic pocket geometry predictor",
    method_type="STRUCTURAL_ALGORITHM",
    edam_operation="EDAM:operation_2575",
    tool="biotools:fpocket",
    evidence_code="ECO:0007669",
    reference="PMID:26950260",
    recipe="fpocket -f {input} -d && mv {input}_out {output}",
)
M_ANOSYM = MethodSpec(
    name="AnAnaS / QuatSym & CE-Symm structural symmetry detection",
    method_type="STRUCTURAL_ALGORITHM",
    edam_operation="EDAM:operation_0248",
    tool="biotools:cesymm",
    evidence_code="ECO:0007669",
    reference="PMID:25260690",
    recipe="anas {input} --sym-group auto -o {output}",
)
M_CESYMM = MethodSpec(
    name="CE-Symm internal repeat & rotational pseudosymmetry detector",
    method_type="STRUCTURAL_ALGORITHM",
    edam_operation="EDAM:operation_0503",
    tool="biotools:cesymm",
    evidence_code="ECO:0007669",
    reference="PMID:25260690",
    recipe="runCESymm.sh {input} -o {output}",
)
M_DEEPCOIL = MethodSpec(
    name="DeepCoil2 / Marcoil / LOGICOIL coiled-coil & oligomeric state predictor",
    method_type="ML_PREDICTOR",
    edam_operation="EDAM:operation_0268",
    tool="biotools:marcoil",
    evidence_code="ECO:0007669",
    reference="PMID:30590416",
    recipe="deepcoil -i {input} -o {output}",
)
M_SOCKET = MethodSpec(
    name="SOCKET2 knobs-into-holes coiled-coil geometry assignment",
    method_type="STRUCTURAL_ALGORITHM",
    edam_operation="EDAM:operation_0268",
    tool="biotools:socket2",
    evidence_code="ECO:0007669",
    reference="PMID:34643705",
    recipe="socket2 -f {input} -c 7.0 -o {output}",
)
M_SIGNALP6 = MethodSpec(
    name="SignalP 6.0 Sec/Tat SPI/SPII/SPIII signal peptide & cleavage predictor",
    method_type="ML_PREDICTOR",
    edam_operation="EDAM:operation_0418",
    tool="biotools:signalp",
    evidence_code="ECO:0000255",
    reference="PMID:34980915",
    recipe="signalp6 --fastafile {input} --output_dir {output} --format txt --organism other",
)
M_TARGETP2 = MethodSpec(
    name="TargetP 2.0 mitochondrial / chloroplast / thylakoid transit peptide predictor",
    method_type="ML_PREDICTOR",
    edam_operation="EDAM:operation_2489",
    tool="biotools:targetp",
    evidence_code="ECO:0000255",
    reference="PMID:31609389",
    recipe="targetp -fasta {input} -org pl -format short -prefix {output}",
)
M_PROPEP = MethodSpec(
    name="ProP 1.0 / InterProScan propeptide cleavage & zymogen domain detector",
    method_type="ML_PREDICTOR",
    edam_operation="EDAM:operation_0422",
    tool="biotools:prop",
    evidence_code="ECO:0000255",
    reference="PMID:15019782",
    recipe="interproscan.sh -i {input} -appl ProSiteProfiles,Pfam -f tsv -o {output}",
)
M_DSSP_SSBOND = MethodSpec(
    name="mkdssp / Geometry-based Sgamma-Sgamma disulfide bond & dihedral χ3 assignment",
    method_type="STRUCTURAL_ALGORITHM",
    edam_operation="EDAM:operation_1836",
    tool="biotools:dssp",
    evidence_code="ECO:0007669",
    reference="PMID:25352545",
    recipe="mkdssp -i {input} -o {output}",
)
M_GO_COMPLEX = MethodSpec(
    name="InterProScan / ComplexPortal GO cellular-component subunit profile scan",
    method_type="HMM_PROFILE",
    edam_operation="EDAM:operation_3672",
    tool="biotools:interproscan",
    evidence_code="ECO:0000265",
    reference="PMID:24451626",
    recipe="interproscan.sh -i {input} -goterms -f tsv -o {output}",
)


SPECS: tuple[TraitSpec, ...] = (
    # --- 1. SEQ_NONSTANDARD_RESIDUE (4 records) ---
    TraitSpec(
        rel_dir="sequence/nonstandard_residue",
        filename="selenocysteine-residue.yaml",
        identifier="proteintraitsmech:NONSTD_SELENOCYSTEINE",
        label="selenocysteine residue",
        definition=(
            "Presence of the genetically encoded 21st amino acid L-selenocysteine (Sec, U), "
            "cotranslationally inserted at an in-frame UGA codon via a selenocysteine insertion "
            "sequence (SECIS) stem-loop RNA element, SelB/EEFSEC elongation factor, and tRNA(Sec)."
        ),
        trait_axis="SEQUENCE",
        trait_category="SEQ_NONSTANDARD_RESIDUE",
        parent_traits=("proteintraitsmech:UNIPROT_FT_NON_STD",),
        synonyms=(
            ("Sec residue", "EXACT_SYNONYM"),
            ("selenocysteine incorporation site", "RELATED_SYNONYM"),
            ("21st amino acid residue", "RELATED_SYNONYM"),
        ),
        xrefs=("SO:0001413", "MOD:00044", "CHEBI:29999"),
        evidence=(("PMID:24070661", "SecMarker identifies SECIS elements and selenoprotein genes across genomes."),),
        detection_methods=(M_SECIS,),
    ),
    TraitSpec(
        rel_dir="sequence/nonstandard_residue",
        filename="pyrrolysine-residue.yaml",
        identifier="proteintraitsmech:NONSTD_PYRROLYSINE",
        label="pyrrolysine residue",
        definition=(
            "Presence of the genetically encoded 22nd amino acid L-pyrrolysine (Pyl, O), a "
            "4-methylpyrroline-5-carboxylate-linked lysine derivative cotranslationally inserted "
            "at an in-frame UAG amber codon by pyrrolysyl-tRNA synthetase (PylRS) and tRNA(Pyl) "
            "in methylotrophic archaea and bacteria."
        ),
        trait_axis="SEQUENCE",
        trait_category="SEQ_NONSTANDARD_RESIDUE",
        parent_traits=("proteintraitsmech:UNIPROT_FT_NON_STD",),
        synonyms=(
            ("Pyl residue", "EXACT_SYNONYM"),
            ("pyrrolysine incorporation site", "RELATED_SYNONYM"),
            ("22nd amino acid residue", "RELATED_SYNONYM"),
        ),
        xrefs=("SO:0001414", "MOD:00869", "CHEBI:32814"),
        evidence=(("PMID:12029132", "Pyrrolysine encoded by the UAG codon in Methanosarcina methylamine methyltransferases."),),
        detection_methods=(M_PYL,),
    ),
    TraitSpec(
        rel_dir="sequence/nonstandard_residue",
        filename="n-formylmethionine-initiator-residue.yaml",
        identifier="proteintraitsmech:NONSTD_N_FORMYLMETHIONINE",
        label="N-formylmethionine initiator residue",
        definition=(
            "Presence of an N-terminal N-formyl-L-methionine (fMet) initiator residue retained "
            "on a bacterial, mitochondrial, or plastid polypeptide when peptide deformylase (PDF) "
            "processing is bypassed or incomplete."
        ),
        trait_axis="SEQUENCE",
        trait_category="SEQ_NONSTANDARD_RESIDUE",
        parent_traits=("proteintraitsmech:UNIPROT_FT_NON_STD", "proteintraitsmech:UNIPROT_FT_INIT_MET"),
        synonyms=(
            ("fMet initiator residue", "EXACT_SYNONYM"),
            ("retained N-formylmethionine", "EXACT_SYNONYM"),
        ),
        xrefs=("MOD:00060", "CHEBI:16714"),
        evidence=(("PMID:16336047", "Specificity of N-terminal formylmethionine retention and peptide deformylase cleavage."),),
        detection_methods=(M_FMET,),
    ),
    TraitSpec(
        rel_dir="sequence/nonstandard_residue",
        filename="post-translationally-epimerized-d-amino-acid-residue.yaml",
        identifier="proteintraitsmech:NONSTD_D_AMINO_ACID_RESIDUE",
        label="post-translationally epimerized D-amino acid residue",
        definition=(
            "Presence of a D-configured alpha-amino acid residue generated in situ from an "
            "L-amino acid residue within a ribosomally translated polypeptide by a peptide "
            "aminoacyl-L/D-epimerase or radical-SAM epimerase."
        ),
        trait_axis="SEQUENCE",
        trait_category="SEQ_NONSTANDARD_RESIDUE",
        parent_traits=("proteintraitsmech:UNIPROT_FT_NON_STD",),
        synonyms=(
            ("ribosomally incorporated D-amino acid residue", "RELATED_SYNONYM"),
            ("epimerized D-residue", "EXACT_SYNONYM"),
        ),
        xrefs=("MOD:00412",),
        evidence=(("PMID:23064350", "Irreversible radical-SAM epimerization introduces multiple D-amino acid residues into proteusin peptides."),),
        detection_methods=(M_DAMINO,),
    ),
    # --- 2. SEQ_LOW_COMPLEXITY (4 records) ---
    TraitSpec(
        rel_dir="sequence/low_complexity",
        filename="low-complexity-sequence-region.yaml",
        identifier="proteintraitsmech:LOWCOMP_REGION",
        label="low-complexity sequence region",
        definition=(
            "A contiguous protein sequence segment whose amino-acid Shannon entropy is "
            "significantly below the proteome background distribution, dominated by one or "
            "a few residue types (as detected by SEG or fLPS segmentation)."
        ),
        trait_axis="SEQUENCE",
        trait_category="SEQ_LOW_COMPLEXITY",
        synonyms=(
            ("LCR", "EXACT_SYNONYM"),
            ("low-complexity region", "EXACT_SYNONYM"),
            ("low-entropy sequence segment", "RELATED_SYNONYM"),
        ),
        xrefs=("SO:0001005",),
        evidence=(
            ("PMID:8306938", "Statistics of local complexity in amino acid sequences and sequence databases (SEG)."),
            ("PMID:28851299", "fLPS fast discovery of compositional biases and low-complexity regions in proteins."),
        ),
        detection_methods=(M_SEG,),
    ),
    TraitSpec(
        rel_dir="sequence/low_complexity",
        filename="homopolymeric-amino-acid-repeat-tract.yaml",
        identifier="proteintraitsmech:LOWCOMP_HOMOREPEAT_TRACT",
        label="homopolymeric amino-acid repeat tract",
        definition=(
            "A single-amino-acid tandem homorepeat run (typically >= 5 consecutive identical "
            "residues, such as polyQ, polyA, polyH, or polyP) forming an extreme low-entropy "
            "tract within a protein sequence."
        ),
        trait_axis="SEQUENCE",
        trait_category="SEQ_LOW_COMPLEXITY",
        parent_traits=("proteintraitsmech:LOWCOMP_REGION",),
        synonyms=(
            ("amino acid homorepeat", "EXACT_SYNONYM"),
            ("homopolymeric tract", "EXACT_SYNONYM"),
            ("single-residue repeat run", "EXACT_SYNONYM"),
        ),
        xrefs=("SO:0001066",),
        evidence=(("PMID:22510761", "Structure, function, and evolution of homorepeats in proteins."),),
        detection_methods=(M_SEG,),
    ),
    TraitSpec(
        rel_dir="sequence/low_complexity",
        filename="prion-like-low-complexity-domain.yaml",
        identifier="proteintraitsmech:LOWCOMP_PRION_LIKE_DOMAIN",
        label="prion-like low-complexity domain",
        definition=(
            "A glutamine/asparagine/tyrosine/glycine-enriched, hydrophobic-depleted low-complexity "
            "sequence domain resembling yeast prion determinants (Sup35, Rnq1, Ure2) that drives "
            "reversible biomolecular condensate assembly or self-templating cross-beta fibrils."
        ),
        trait_axis="SEQUENCE",
        trait_category="SEQ_LOW_COMPLEXITY",
        parent_traits=("proteintraitsmech:LOWCOMP_REGION", "IDPO:00076"),
        synonyms=(
            ("PrLD", "EXACT_SYNONYM"),
            ("prion-like domain", "EXACT_SYNONYM"),
            ("Q/N-rich prion-like low-complexity region", "RELATED_SYNONYM"),
        ),
        evidence=(
            ("PMID:24667259", "PLAAC: a web and command-line application to scan forigh-probability prion-like domains."),
            ("PMID:25891072", "Prion-like domains in RNA-binding proteins are essential for phase separation and stress granules."),
        ),
        detection_methods=(M_PLAAC, M_SEG),
    ),
    TraitSpec(
        rel_dir="sequence/low_complexity",
        filename="cryptic-short-periodicity-low-complexity-region.yaml",
        identifier="proteintraitsmech:LOWCOMP_CRYPTIC_REPEAT_REGION",
        label="cryptic short-periodicity low-complexity region",
        definition=(
            "A low-complexity region composed of degenerate di-, tri-, or tetrapeptide repeats "
            "(such as RG/RGG, YG/SYGQ, FG, or KSPEA motifs) that lacks strict tandem repeat "
            "regularity yet maintains strongly reduced sequence entropy."
        ),
        trait_axis="SEQUENCE",
        trait_category="SEQ_LOW_COMPLEXITY",
        parent_traits=("proteintraitsmech:LOWCOMP_REGION",),
        synonyms=(
            ("cryptic repeat LCR", "EXACT_SYNONYM"),
            ("quasi-repetitive low-complexity region", "EXACT_SYNONYM"),
        ),
        evidence=(("PMID:28851299", "fLPS characterizes both single-residue and multi-residue cryptic compositional biases."),),
        detection_methods=(M_SEG,),
    ),
    # --- 3. SEQ_COMPOSITION (10 records) ---
    TraitSpec(
        rel_dir="sequence/composition",
        filename="polyglutamine-tract.yaml",
        identifier="proteintraitsmech:COMPBIAS_POLYGLUTAMINE_TRACT",
        label="polyglutamine tract",
        definition=(
            "A glutamine-biased homopolymeric sequence region (typically >= 8 consecutive or "
            "near-consecutive Gln residues) that modulates transcriptional coactivator interactions "
            "and, above pathogenic length thresholds, nucleates cross-beta amyloid aggregation."
        ),
        trait_axis="SEQUENCE",
        trait_category="SEQ_COMPOSITION",
        parent_traits=("proteintraitsmech:LOWCOMP_HOMOREPEAT_TRACT",),
        synonyms=(
            ("polyQ tract", "EXACT_SYNONYM"),
            ("poly-Gln region", "EXACT_SYNONYM"),
            ("glutamine-rich homorepeat", "RELATED_SYNONYM"),
        ),
        sequence_pattern="Q{8,}",
        evidence=(("PMID:22510761", "Polyglutamine tracts are among the most prevalent functional and pathogenic homorepeats in eukaryotes."),),
        detection_methods=(M_FLPS,),
    ),
    TraitSpec(
        rel_dir="sequence/composition",
        filename="polyalanine-tract.yaml",
        identifier="proteintraitsmech:COMPBIAS_POLYALANINE_TRACT",
        label="polyalanine tract",
        definition=(
            "An alanine-biased homopolymeric sequence tract (typically >= 7 consecutive Ala "
            "residues) common in transcription factors and RNA-binding proteins, where it forms "
            "alpha-helical spacers and can misfold upon tract expansion."
        ),
        trait_axis="SEQUENCE",
        trait_category="SEQ_COMPOSITION",
        parent_traits=("proteintraitsmech:LOWCOMP_HOMOREPEAT_TRACT",),
        synonyms=(
            ("polyA tract", "EXACT_SYNONYM"),
            ("poly-Ala region", "EXACT_SYNONYM"),
        ),
        sequence_pattern="A{7,}",
        evidence=(("PMID:15520409", "Polyalanine tract expansions in transcription factors cause developmental disorders via misfolding."),),
        detection_methods=(M_FLPS,),
    ),
    TraitSpec(
        rel_dir="sequence/composition",
        filename="histidine-rich-region.yaml",
        identifier="proteintraitsmech:COMPBIAS_HISTIDINE_RICH_REGION",
        label="histidine-rich region",
        definition=(
            "A compositionally biased protein region significantly enriched in L-histidine "
            "residues (including polyHis runs and His-X repeats), conferring pH-responsive "
            "protonation switching, divalent transition-metal (Ni2+, Zn2+, Cu2+) coordination, "
            "or subnuclear speckle targeting."
        ),
        trait_axis="SEQUENCE",
        trait_category="SEQ_COMPOSITION",
        parent_traits=("proteintraitsmech:LOWCOMP_REGION",),
        synonyms=(
            ("His-rich region", "EXACT_SYNONYM"),
            ("polyhistidine-enriched region", "RELATED_SYNONYM"),
        ),
        sequence_pattern="H{5,}",
        evidence=(("PMID:28851299", "Discovery of histidine-rich compositional biases in proteomes using fLPS."),),
        detection_methods=(M_FLPS,),
    ),
    TraitSpec(
        rel_dir="sequence/composition",
        filename="cysteine-rich-region.yaml",
        identifier="proteintraitsmech:COMPBIAS_CYSTEINE_RICH_REGION",
        label="cysteine-rich region",
        definition=(
            "A compositionally biased protein region enriched in L-cysteine residues that "
            "supports high-density disulfide crosslinking (as in keratins, defensins, and "
            "extracellular matrix modules) or polynuclear metal-thiolate cluster coordination "
            "(as in metallothioneins)."
        ),
        trait_axis="SEQUENCE",
        trait_category="SEQ_COMPOSITION",
        parent_traits=("proteintraitsmech:LOWCOMP_REGION",),
        synonyms=(
            ("Cys-rich region", "EXACT_SYNONYM"),
            ("cysteine-enriched domain", "RELATED_SYNONYM"),
        ),
        evidence=(("PMID:19569188", "Classification and functional architecture of cysteine-rich protein domains."),),
        detection_methods=(M_FLPS,),
    ),
    TraitSpec(
        rel_dir="sequence/composition",
        filename="proline-rich-region.yaml",
        identifier="proteintraitsmech:COMPBIAS_PROLINE_RICH_REGION",
        label="proline-rich region",
        definition=(
            "A compositionally biased protein segment enriched in L-proline residues that "
            "favors extended polyproline II (PPII) left-handed helical conformations and "
            "serves as a recognition scaffold for SH3, WW, EVH1, and profilin domains."
        ),
        trait_axis="SEQUENCE",
        trait_category="SEQ_COMPOSITION",
        parent_traits=("proteintraitsmech:LOWCOMP_REGION",),
        synonyms=(
            ("Pro-rich region", "EXACT_SYNONYM"),
            ("PRR", "RELATED_SYNONYM"),
            ("polyproline-rich region", "RELATED_SYNONYM"),
        ),
        evidence=(("PMID:15698841", "Proline-rich regions and polyproline II helices in protein-protein recognition."),),
        detection_methods=(M_FLPS,),
    ),
    TraitSpec(
        rel_dir="sequence/composition",
        filename="glycine-rich-region.yaml",
        identifier="proteintraitsmech:COMPBIAS_GLYCINE_RICH_REGION",
        label="glycine-rich region",
        definition=(
            "A compositionally biased protein region enriched in achiral glycine residues "
            "(including GGG, GGX, and RGG/YG tracts) that imparts high backbone conformational "
            "entropy, flexible linker dynamics, or beta-sheet/fibril packing."
        ),
        trait_axis="SEQUENCE",
        trait_category="SEQ_COMPOSITION",
        parent_traits=("proteintraitsmech:LOWCOMP_REGION",),
        synonyms=(
            ("Gly-rich region", "EXACT_SYNONYM"),
            ("glycine-enriched region", "EXACT_SYNONYM"),
        ),
        evidence=(("PMID:24240281", "RGG/RG and glycine-rich motifs in RNA binding, phase separation, and cell signaling."),),
        detection_methods=(M_FLPS,),
    ),
    TraitSpec(
        rel_dir="sequence/composition",
        filename="serine-threonine-rich-region.yaml",
        identifier="proteintraitsmech:COMPBIAS_SERINE_THREONINE_RICH_REGION",
        label="serine/threonine-rich region",
        definition=(
            "A compositionally biased hydroxyl-rich sequence region enriched in L-serine and/or "
            "L-threonine residues (including mucin-like PTS domains and SR-protein RS domains), "
            "frequently serving as a dense substrate for O-glycosylation or multisite phosphorylation."
        ),
        trait_axis="SEQUENCE",
        trait_category="SEQ_COMPOSITION",
        parent_traits=("proteintraitsmech:LOWCOMP_REGION",),
        synonyms=(
            ("Ser/Thr-rich region", "EXACT_SYNONYM"),
            ("S/T-rich region", "EXACT_SYNONYM"),
        ),
        evidence=(("PMID:28851299", "fLPS compositional bias detection identifies Ser/Thr-rich mucin and signaling regions."),),
        detection_methods=(M_FLPS,),
    ),
    TraitSpec(
        rel_dir="sequence/composition",
        filename="acidic-negatively-charged-region.yaml",
        identifier="proteintraitsmech:COMPBIAS_ACIDIC_REGION",
        label="acidic negatively charged region",
        definition=(
            "A compositionally biased protein segment enriched in aspartate and glutamate "
            "(D/E-rich tract) with high net negative charge density, mediating histone "
            "chaperoning, DNA mimicry, calcium buffering, or transcriptional activation."
        ),
        trait_axis="SEQUENCE",
        trait_category="SEQ_COMPOSITION",
        parent_traits=("proteintraitsmech:LOWCOMP_REGION",),
        synonyms=(
            ("Asp/Glu-rich region", "EXACT_SYNONYM"),
            ("D/E-rich acidic tract", "EXACT_SYNONYM"),
            ("polyanionic sequence region", "RELATED_SYNONYM"),
        ),
        evidence=(("PMID:28851299", "Binomial compositional bias detection of D/E-rich acidic tracts."),),
        detection_methods=(M_FLPS,),
    ),
    TraitSpec(
        rel_dir="sequence/composition",
        filename="basic-positively-charged-region.yaml",
        identifier="proteintraitsmech:COMPBIAS_BASIC_REGION",
        label="basic positively charged region",
        definition=(
            "A compositionally biased protein segment enriched in lysine and arginine "
            "(K/R-rich tract) with high net positive charge density, mediating nucleic-acid "
            "backbone binding, nuclear/nucleolar localization, or anionic membrane association."
        ),
        trait_axis="SEQUENCE",
        trait_category="SEQ_COMPOSITION",
        parent_traits=("proteintraitsmech:LOWCOMP_REGION",),
        synonyms=(
            ("Lys/Arg-rich region", "EXACT_SYNONYM"),
            ("K/R-rich basic tract", "EXACT_SYNONYM"),
            ("polycationic sequence region", "RELATED_SYNONYM"),
        ),
        evidence=(("PMID:28851299", "Binomial compositional bias detection of K/R-rich basic regions."),),
        detection_methods=(M_FLPS,),
    ),
    TraitSpec(
        rel_dir="sequence/composition",
        filename="aromatic-polar-sticker-spacer-region.yaml",
        identifier="proteintraitsmech:COMPBIAS_AROMATIC_POLAR_STICKER_SPACER",
        label="aromatic-polar sticker-and-spacer region",
        definition=(
            "A compositionally biased intrinsically disordered region featuring regularly "
            "spaced aromatic 'sticker' residues (Tyr, Phe, Trp) embedded in a polar Gly/Ser/Gln "
            "'spacer' matrix that governs cation-pi and pi-pi phase separation."
        ),
        trait_axis="SEQUENCE",
        trait_category="SEQ_COMPOSITION",
        parent_traits=("proteintraitsmech:LOWCOMP_REGION", "IDPO:00076"),
        synonyms=(
            ("Tyr/Phe sticker-spacer LCD", "EXACT_SYNONYM"),
            ("aromatic-spaced low-complexity domain", "EXACT_SYNONYM"),
        ),
        evidence=(("PMID:29961577", "Valence and patterning of aromatic stickers and polar spacers determine phase behavior of PLD proteins."),),
        detection_methods=(M_FLPS,),
    ),
    # --- 4. STRUCT_QUATERNARY (11 records) ---
    TraitSpec(
        rel_dir="structure/quaternary",
        filename="monomeric-quaternary-structure.yaml",
        identifier="proteintraitsmech:QUATERNARY_MONOMER",
        label="monomeric quaternary structure",
        definition=(
            "A biological assembly state in which the functional macromolecular unit consists "
            "of a single folded polypeptide chain (stoichiometry A1) without stable oligomeric "
            "subunit interfaces in solution."
        ),
        trait_axis="STRUCTURE",
        trait_category="STRUCT_QUATERNARY",
        synonyms=(
            ("monomer", "EXACT_SYNONYM"),
            ("monomeric protein assembly", "EXACT_SYNONYM"),
            ("A1 stoichiometry", "RELATED_SYNONYM"),
        ),
        evidence=(("PMID:16537912", "Structural classification and evolution of protein quaternary structure: monomers and oligomers."),),
        detection_methods=(M_PISA,),
    ),
    TraitSpec(
        rel_dir="structure/quaternary",
        filename="homodimeric-quaternary-structure.yaml",
        identifier="proteintraitsmech:QUATERNARY_HOMODIMER",
        label="homodimeric quaternary structure",
        definition=(
            "A quaternary assembly composed of two identical polypeptide subunits (stoichiometry A2), "
            "typically related by a two-fold (C2) rotational symmetry axis across an isologous "
            "dimer interface."
        ),
        trait_axis="STRUCTURE",
        trait_category="STRUCT_QUATERNARY",
        synonyms=(
            ("homodimer", "EXACT_SYNONYM"),
            ("A2 homodimeric assembly", "EXACT_SYNONYM"),
        ),
        xrefs=("GO:0042803",),
        evidence=(("PMID:17681537", "Inference of macromolecular assemblies from crystalline state via PDBePISA."),),
        detection_methods=(M_PISA,),
    ),
    TraitSpec(
        rel_dir="structure/quaternary",
        filename="heterodimeric-quaternary-structure.yaml",
        identifier="proteintraitsmech:QUATERNARY_HETERODIMER",
        label="heterodimeric quaternary structure",
        definition=(
            "A quaternary assembly composed of two non-identical polypeptide chains "
            "(stoichiometry AB) joined across a specific asymmetric macromolecular interface."
        ),
        trait_axis="STRUCTURE",
        trait_category="STRUCT_QUATERNARY",
        synonyms=(
            ("heterodimer", "EXACT_SYNONYM"),
            ("AB heterodimeric assembly", "EXACT_SYNONYM"),
        ),
        xrefs=("GO:0046982",),
        evidence=(("PMID:17681537", "PDBePISA macromolecular interface and assembly stoichiometry determination."),),
        detection_methods=(M_PISA,),
    ),
    TraitSpec(
        rel_dir="structure/quaternary",
        filename="homotrimeric-quaternary-structure.yaml",
        identifier="proteintraitsmech:QUATERNARY_HOMOTRIMER",
        label="homotrimeric quaternary structure",
        definition=(
            "A quaternary assembly composed of three identical polypeptide subunits "
            "(stoichiometry A3), canonically arranged around a three-fold cyclic (C3) axis "
            "via heterologous head-to-tail subunit interfaces."
        ),
        trait_axis="STRUCTURE",
        trait_category="STRUCT_QUATERNARY",
        synonyms=(
            ("homotrimer", "EXACT_SYNONYM"),
            ("A3 homotrimeric assembly", "EXACT_SYNONYM"),
        ),
        evidence=(("PMID:16537912", "Evolutionary and structural principles of protein oligomeric complexes."),),
        detection_methods=(M_PISA,),
    ),
    TraitSpec(
        rel_dir="structure/quaternary",
        filename="heterotrimeric-quaternary-structure.yaml",
        identifier="proteintraitsmech:QUATERNARY_HETEROTRIMER",
        label="heterotrimeric quaternary structure",
        definition=(
            "A quaternary assembly composed of three polypeptide chains from two or three "
            "distinct subunit types (stoichiometry A2B or ABC, such as heterotrimeric G-proteins)."
        ),
        trait_axis="STRUCTURE",
        trait_category="STRUCT_QUATERNARY",
        synonyms=(
            ("heterotrimer", "EXACT_SYNONYM"),
            ("ABC / A2B heterotrimeric assembly", "RELATED_SYNONYM"),
        ),
        evidence=(("PMID:16537912", "Classification of hetero-oligomeric quaternary assemblies by subunit stoichiometry."),),
        detection_methods=(M_PISA,),
    ),
    TraitSpec(
        rel_dir="structure/quaternary",
        filename="homotetrameric-quaternary-structure.yaml",
        identifier="proteintraitsmech:QUATERNARY_HOMOTETRAMER",
        label="homotetrameric quaternary structure",
        definition=(
            "A quaternary assembly composed of four identical polypeptide subunits "
            "(stoichiometry A4), most commonly adopting dihedral D2 (dimer-of-dimers) "
            "or cyclic C4 ring architecture."
        ),
        trait_axis="STRUCTURE",
        trait_category="STRUCT_QUATERNARY",
        synonyms=(
            ("homotetramer", "EXACT_SYNONYM"),
            ("A4 homotetrameric assembly", "EXACT_SYNONYM"),
        ),
        evidence=(("PMID:16537912", "Dimer-of-dimers D2 and cyclic C4 homotetramers in the Protein Data Bank."),),
        detection_methods=(M_PISA,),
    ),
    TraitSpec(
        rel_dir="structure/quaternary",
        filename="heterotetrameric-quaternary-structure.yaml",
        identifier="proteintraitsmech:QUATERNARY_HETEROTETRAMER",
        label="heterotetrameric quaternary structure",
        definition=(
            "A quaternary assembly of four polypeptide chains comprising at least two distinct "
            "subunit types (commonly A2B2 dimer-of-heterodimers, such as alpha2-beta2 hemoglobin "
            "or tryptophan synthase)."
        ),
        trait_axis="STRUCTURE",
        trait_category="STRUCT_QUATERNARY",
        synonyms=(
            ("heterotetramer", "EXACT_SYNONYM"),
            ("A2B2 heterotetrameric assembly", "RELATED_SYNONYM"),
        ),
        evidence=(("PMID:16537912", "Periodic table of protein complexes and A2B2 heterotetramer assembly pathways."),),
        detection_methods=(M_PISA,),
    ),
    TraitSpec(
        rel_dir="structure/quaternary",
        filename="homopentameric-quaternary-structure.yaml",
        identifier="proteintraitsmech:QUATERNARY_HOMOPENTAMER",
        label="homopentameric quaternary structure",
        definition=(
            "A quaternary assembly composed of five identical polypeptide subunits "
            "(stoichiometry A5) arranged in a closed C5 cyclic ring, characteristic of "
            "pentameric ligand-gated ion channels, mechanosensitive channels, and AB5 toxin B-subunits."
        ),
        trait_axis="STRUCTURE",
        trait_category="STRUCT_QUATERNARY",
        synonyms=(
            ("homopentamer", "EXACT_SYNONYM"),
            ("A5 homopentameric ring", "EXACT_SYNONYM"),
        ),
        evidence=(("PMID:16537912", "Cyclic C5 homopentameric assemblies in membrane pores and soluble complexes."),),
        detection_methods=(M_PISA,),
    ),
    TraitSpec(
        rel_dir="structure/quaternary",
        filename="homohexameric-quaternary-structure.yaml",
        identifier="proteintraitsmech:QUATERNARY_HOMOHEXAMER",
        label="homohexameric quaternary structure",
        definition=(
            "A quaternary assembly composed of six identical polypeptide subunits "
            "(stoichiometry A6), adopting either a cyclic C6 ring (such as AAA+ ATPases "
            "and replicative helicases) or a dihedral D3 trimer-of-dimers."
        ),
        trait_axis="STRUCTURE",
        trait_category="STRUCT_QUATERNARY",
        synonyms=(
            ("homohexamer", "EXACT_SYNONYM"),
            ("A6 homohexameric assembly", "EXACT_SYNONYM"),
        ),
        evidence=(("PMID:16537912", "C6 ring and D3 dihedral homohexameric architectures."),),
        detection_methods=(M_PISA,),
    ),
    TraitSpec(
        rel_dir="structure/quaternary",
        filename="cage-forming-homo-oligomeric-quaternary-structure.yaml",
        identifier="proteintraitsmech:QUATERNARY_HOMO_OLIGOMER_CAGE",
        label="cage-forming homo-oligomeric quaternary structure",
        definition=(
            "A high-order closed polyhedral quaternary shell (such as 12-mer tetrahedral, "
            "24-mer octahedral ferritin, or 60-mer icosahedral encapsulin/lumazine synthase cages) "
            "enclosing an internal nanoscale cavity."
        ),
        trait_axis="STRUCTURE",
        trait_category="STRUCT_QUATERNARY",
        synonyms=(
            ("polyhedral protein cage", "EXACT_SYNONYM"),
            ("nanocage quaternary assembly", "EXACT_SYNONYM"),
        ),
        evidence=(("PMID:16537912", "Tetrahedral, octahedral, and icosahedral self-assembling protein cages."),),
        detection_methods=(M_PISA,),
    ),
    TraitSpec(
        rel_dir="structure/quaternary",
        filename="helical-filament-polymeric-quaternary-structure.yaml",
        identifier="proteintraitsmech:QUATERNARY_HELICAL_FILAMENT",
        label="helical filament polymeric quaternary structure",
        definition=(
            "An open-ended or length-regulated non-covalent polymeric quaternary assembly in "
            "which protomers repeat along a screw axis (helical symmetry), as in cytoskeletal "
            "filaments, recombinase nucleoprotein filaments, and metabolic cytoophidia."
        ),
        trait_axis="STRUCTURE",
        trait_category="STRUCT_QUATERNARY",
        synonyms=(
            ("helical protein polymer", "EXACT_SYNONYM"),
            ("filamentous quaternary assembly", "EXACT_SYNONYM"),
        ),
        evidence=(("PMID:29688318", "Filamentation of metabolic enzymes and structural mechanisms of helical polymerization."),),
        detection_methods=(M_PISA,),
    ),
    # --- 5. STRUCT_ALLOSTERIC_SITE (5 records) ---
    TraitSpec(
        rel_dir="structure/allosteric_site",
        filename="allosteric-regulatory-site.yaml",
        identifier="proteintraitsmech:ALLOSTERIC_REGULATORY_SITE",
        label="allosteric regulatory site",
        definition=(
            "A topographically distinct ligand- or effector-binding pocket, physically separate "
            "from the orthosteric active or substrate-binding site, whose occupancy shifts the "
            "conformational ensemble or dynamic coupling of the protein to modulate functional activity."
        ),
        trait_axis="STRUCTURE",
        trait_category="STRUCT_ALLOSTERIC_SITE",
        parent_traits=("proteintraitsmech:BINDING_SITE",),
        synonyms=(
            ("allosteric site", "EXACT_SYNONYM"),
            ("allosteric effector pocket", "EXACT_SYNONYM"),
        ),
        evidence=(
            ("PMID:20971780", "ASD: a comprehensive database of allosteric proteins and modulators."),
            ("PMID:18722889", "The conformational spread and ensemble view of allostery in proteins."),
        ),
        detection_methods=(M_FPOCKET,),
    ),
    TraitSpec(
        rel_dir="structure/allosteric_site",
        filename="allosteric-activator-site.yaml",
        identifier="proteintraitsmech:ALLOSTERIC_ACTIVATOR_SITE",
        label="allosteric activator site",
        definition=(
            "An allosteric regulatory pocket whose binding by a positive effector stabilizes "
            "the high-affinity or catalytically competent (R-state) conformation, increasing "
            "substrate affinity (K-type) or catalytic turnover (V-type)."
        ),
        trait_axis="STRUCTURE",
        trait_category="STRUCT_ALLOSTERIC_SITE",
        parent_traits=("proteintraitsmech:ALLOSTERIC_REGULATORY_SITE",),
        synonyms=(
            ("positive allosteric modulator site", "EXACT_SYNONYM"),
            ("PAM binding site", "RELATED_SYNONYM"),
        ),
        evidence=(("PMID:20971780", "Classification of positive allosteric activator sites in ASD."),),
        detection_methods=(M_FPOCKET,),
    ),
    TraitSpec(
        rel_dir="structure/allosteric_site",
        filename="allosteric-inhibitor-site.yaml",
        identifier="proteintraitsmech:ALLOSTERIC_INHIBITOR_SITE",
        label="allosteric inhibitor site",
        definition=(
            "An allosteric regulatory pocket whose occupancy by a negative effector or feedback "
            "inhibitor stabilizes a low-affinity or catalytically autoinhibited (T-state) "
            "conformation, reducing orthosteric activity non-competitively."
        ),
        trait_axis="STRUCTURE",
        trait_category="STRUCT_ALLOSTERIC_SITE",
        parent_traits=("proteintraitsmech:ALLOSTERIC_REGULATORY_SITE",),
        synonyms=(
            ("negative allosteric modulator site", "EXACT_SYNONYM"),
            ("NAM binding site", "RELATED_SYNONYM"),
            ("feedback inhibition allosteric site", "RELATED_SYNONYM"),
        ),
        evidence=(("PMID:20971780", "Structural mechanisms of negative allosteric inhibition across enzyme families."),),
        detection_methods=(M_FPOCKET,),
    ),
    TraitSpec(
        rel_dir="structure/allosteric_site",
        filename="cryptic-allosteric-pocket.yaml",
        identifier="proteintraitsmech:ALLOSTERIC_CRYPTIC_POCKET",
        label="cryptic allosteric pocket",
        definition=(
            "A transient allosteric binding cavity that is occluded or absent in the unliganded "
            "ground-state structure and opens only through thermal conformational fluctuations "
            "or induced-fit side-chain/loop rearrangements upon ligand encounter."
        ),
        trait_axis="STRUCTURE",
        trait_category="STRUCT_ALLOSTERIC_SITE",
        parent_traits=("proteintraitsmech:ALLOSTERIC_REGULATORY_SITE",),
        synonyms=(
            ("cryptic binding pocket", "EXACT_SYNONYM"),
            ("transient allosteric cavity", "EXACT_SYNONYM"),
        ),
        evidence=(("PMID:36973262", "PocketMiner and CryptoSite reveal cryptic pockets across the proteome."),),
        detection_methods=(M_FPOCKET,),
    ),
    TraitSpec(
        rel_dir="structure/allosteric_site",
        filename="subunit-interface-allosteric-site.yaml",
        identifier="proteintraitsmech:ALLOSTERIC_SUBUNIT_INTERFACE_SITE",
        label="subunit-interface allosteric site",
        definition=(
            "An allosteric regulatory site situated at the inter-protomer boundary of an "
            "oligomeric protein complex, where effector binding couples quaternary subunit "
            "rotation directly to cooperative transitions across multiple active sites."
        ),
        trait_axis="STRUCTURE",
        trait_category="STRUCT_ALLOSTERIC_SITE",
        parent_traits=("proteintraitsmech:ALLOSTERIC_REGULATORY_SITE", "proteintraitsmech:PROTEIN_INTERFACE"),
        synonyms=(
            ("inter-subunit allosteric pocket", "EXACT_SYNONYM"),
            ("quaternary interface allosteric site", "EXACT_SYNONYM"),
        ),
        evidence=(("PMID:23624396", "Allosteric regulation at protein-protein and subunit interfaces."),),
        detection_methods=(M_FPOCKET,),
    ),
    # --- 6. STRUCT_SYMMETRY (9 records) ---
    TraitSpec(
        rel_dir="structure/symmetry",
        filename="asymmetric-c1-point-group.yaml",
        identifier="proteintraitsmech:SYMMETRY_ASYMMETRIC_C1",
        label="asymmetric (C1) structural point group",
        definition=(
            "Absence of global rotational, dihedral, cubic, or helical symmetry operations "
            "(Schoenflies point group C1), characteristic of monomeric proteins and asymmetric "
            "hetero-oligomeric complexes."
        ),
        trait_axis="STRUCTURE",
        trait_category="STRUCT_SYMMETRY",
        synonyms=(
            ("C1 point group symmetry", "EXACT_SYNONYM"),
            ("asymmetric macromolecular architecture", "EXACT_SYNONYM"),
        ),
        evidence=(("PMID:10666789", "Structural symmetry and asymmetry in proteins (Goodsell & Olson 2000)."),),
        detection_methods=(M_ANOSYM,),
    ),
    TraitSpec(
        rel_dir="structure/symmetry",
        filename="cyclic-cn-rotational-symmetry.yaml",
        identifier="proteintraitsmech:SYMMETRY_CYCLIC_CN",
        label="cyclic (Cn) rotational symmetry",
        definition=(
            "Global closed rotational symmetry of Schoenflies group Cn (n >= 2), in which "
            "n protomers are related by 360/n-degree rotations around a single central symmetry axis."
        ),
        trait_axis="STRUCTURE",
        trait_category="STRUCT_SYMMETRY",
        synonyms=(
            ("Cn point group symmetry", "EXACT_SYNONYM"),
            ("cyclic rotational symmetry", "EXACT_SYNONYM"),
        ),
        evidence=(("PMID:10666789", "Cyclic Cn symmetry in soluble and membrane-associated protein oligomers."),),
        detection_methods=(M_ANOSYM,),
    ),
    TraitSpec(
        rel_dir="structure/symmetry",
        filename="two-fold-cyclic-c2-symmetry.yaml",
        identifier="proteintraitsmech:SYMMETRY_CYCLIC_C2",
        label="two-fold cyclic (C2) rotational symmetry",
        definition=(
            "Cyclic symmetry of order 2 (Schoenflies C2) in which two subunits or pseudo-symmetric "
            "halves are related by a 180-degree rotation around a single dyad axis across an "
            "isologous interface."
        ),
        trait_axis="STRUCTURE",
        trait_category="STRUCT_SYMMETRY",
        parent_traits=("proteintraitsmech:SYMMETRY_CYCLIC_CN",),
        synonyms=(
            ("C2 dyad symmetry", "EXACT_SYNONYM"),
            ("two-fold rotational symmetry", "EXACT_SYNONYM"),
        ),
        evidence=(("PMID:10666789", "C2 dyad symmetry is the most abundant oligomeric point group in proteins."),),
        detection_methods=(M_ANOSYM,),
    ),
    TraitSpec(
        rel_dir="structure/symmetry",
        filename="three-fold-cyclic-c3-symmetry.yaml",
        identifier="proteintraitsmech:SYMMETRY_CYCLIC_C3",
        label="three-fold cyclic (C3) rotational symmetry",
        definition=(
            "Cyclic symmetry of order 3 (Schoenflies C3) in which three protomers or structural "
            "repeats are related by 120-degree rotations around a central triad axis."
        ),
        trait_axis="STRUCTURE",
        trait_category="STRUCT_SYMMETRY",
        parent_traits=("proteintraitsmech:SYMMETRY_CYCLIC_CN",),
        synonyms=(
            ("C3 triad symmetry", "EXACT_SYNONYM"),
            ("three-fold rotational symmetry", "EXACT_SYNONYM"),
        ),
        evidence=(("PMID:10666789", "C3 symmetry in homotrimeric spikes, porins, and fibrous proteins."),),
        detection_methods=(M_ANOSYM,),
    ),
    TraitSpec(
        rel_dir="structure/symmetry",
        filename="dihedral-dn-symmetry.yaml",
        identifier="proteintraitsmech:SYMMETRY_DIHEDRAL_DN",
        label="dihedral (Dn) point-group symmetry",
        definition=(
            "Global closed symmetry of Schoenflies group Dn (n >= 2), combining an n-fold "
            "principal rotational axis with n perpendicular two-fold (C2) dyad axes, formed "
            "by stacking two Cn rings face-to-face or assembling n dimers."
        ),
        trait_axis="STRUCTURE",
        trait_category="STRUCT_SYMMETRY",
        synonyms=(
            ("Dn point group symmetry", "EXACT_SYNONYM"),
            ("dihedral macromolecular symmetry", "EXACT_SYNONYM"),
        ),
        evidence=(("PMID:10666789", "Dihedral Dn symmetry dominates soluble metabolic enzymes of 4 or more subunits."),),
        detection_methods=(M_ANOSYM,),
    ),
    TraitSpec(
        rel_dir="structure/symmetry",
        filename="dihedral-d2-tetrahedral-dyad-symmetry.yaml",
        identifier="proteintraitsmech:SYMMETRY_DIHEDRAL_D2",
        label="dihedral (D2) dimer-of-dimers symmetry",
        definition=(
            "Dihedral symmetry of order 2 (Schoenflies D2) featuring three mutually perpendicular "
            "two-fold rotational axes, the canonical symmetry of dimer-of-dimers homotetramers "
            "and A2B2 heterotetramers."
        ),
        trait_axis="STRUCTURE",
        trait_category="STRUCT_SYMMETRY",
        parent_traits=("proteintraitsmech:SYMMETRY_DIHEDRAL_DN",),
        synonyms=(
            ("D2 symmetry", "EXACT_SYNONYM"),
            ("orthorhombic three-dyad symmetry", "RELATED_SYNONYM"),
        ),
        evidence=(("PMID:16537912", "Evolution of D2 dihedral tetramers from C2 dimers via a second isologous interface."),),
        detection_methods=(M_ANOSYM,),
    ),
    TraitSpec(
        rel_dir="structure/symmetry",
        filename="cubic-polyhedral-symmetry.yaml",
        identifier="proteintraitsmech:SYMMETRY_CUBIC_POLYHEDRAL",
        label="cubic polyhedral (T / O / I) symmetry",
        definition=(
            "High-order closed point-group symmetry combining three-fold and two-fold axes "
            "with four-fold or five-fold axes — tetrahedral (T, 12 subunits), octahedral "
            "(O, 24 subunits), or icosahedral (I, 60n subunits)."
        ),
        trait_axis="STRUCTURE",
        trait_category="STRUCT_SYMMETRY",
        synonyms=(
            ("tetrahedral/octahedral/icosahedral symmetry", "EXACT_SYNONYM"),
            ("platonic polyhedral symmetry", "RELATED_SYNONYM"),
        ),
        evidence=(("PMID:10666789", "Tetrahedral, octahedral, and icosahedral point groups in spherical protein shells."),),
        detection_methods=(M_ANOSYM,),
    ),
    TraitSpec(
        rel_dir="structure/symmetry",
        filename="helical-screw-symmetry.yaml",
        identifier="proteintraitsmech:SYMMETRY_HELICAL_H",
        label="helical (H) screw-axis symmetry",
        definition=(
            "Open-ended symmetry in which protomers are related by a coupled rotation (twist) "
            "and axial translation (rise) along a central screw axis, generating filamentous "
            "or tubular assemblies."
        ),
        trait_axis="STRUCTURE",
        trait_category="STRUCT_SYMMETRY",
        synonyms=(
            ("helical symmetry", "EXACT_SYNONYM"),
            ("screw-axis symmetry", "EXACT_SYNONYM"),
        ),
        evidence=(("PMID:10666789", "Helical line-group symmetry in protein filaments and tubules."),),
        detection_methods=(M_ANOSYM,),
    ),
    TraitSpec(
        rel_dir="structure/symmetry",
        filename="internal-tertiary-pseudosymmetry.yaml",
        identifier="proteintraitsmech:SYMMETRY_INTERNAL_PSEUDOSYMMETRY",
        label="internal tertiary rotational pseudosymmetry",
        definition=(
            "Approximate rotational or translational symmetry *within* a single polypeptide "
            "chain (such as C8 beta-propellers, (beta/alpha)8 TIM barrels, C3 beta-trefoils, "
            "or inverted-topology membrane transporters) arising from intragenic duplication "
            "and fusion."
        ),
        trait_axis="STRUCTURE",
        trait_category="STRUCT_SYMMETRY",
        synonyms=(
            ("internal structural symmetry", "EXACT_SYNONYM"),
            ("tertiary pseudosymmetry", "EXACT_SYNONYM"),
            ("intrachain rotational pseudosymmetry", "EXACT_SYNONYM"),
        ),
        evidence=(("PMID:25260690", "CE-Symm detects internal symmetry and pseudosymmetry in monomeric protein structures."),),
        detection_methods=(M_CESYMM,),
    ),
    # --- 7. MIXED_COILED_COIL (7 records) ---
    TraitSpec(
        rel_dir="sequence_structure/coiled_coil",
        filename="heptad-repeat-coiled-coil-segment.yaml",
        identifier="proteintraitsmech:COILED_COIL_HEPTAD_REPEAT",
        label="heptad-repeat coiled-coil segment",
        definition=(
            "A supercoiled alpha-helical bundle motif defined at the sequence level by a "
            "seven-residue (abcdefg)n heptad periodicity with hydrophobic residues at core "
            "positions a and d and polar/charged residues at e and g, packing via Crick "
            "knobs-into-holes geometry."
        ),
        trait_axis="SEQUENCE_STRUCTURE",
        trait_category="MIXED_COILED_COIL",
        parent_traits=("proteintraitsmech:COILED_COIL",),
        synonyms=(
            ("canonical (abcdefg)n coiled coil", "EXACT_SYNONYM"),
            ("knobs-into-holes heptad coiled coil", "EXACT_SYNONYM"),
        ),
        xrefs=("SO:0001080",),
        evidence=(
            ("PMID:28118746", "Sequence-to-structure rules of heptad and non-heptad coiled coils (Woolfson 2017)."),
            ("PMID:34643705", "SOCKET2: geometric identification of knobs-into-holes packing in coiled coils."),
        ),
        detection_methods=(M_DEEPCOIL, M_SOCKET),
    ),
    TraitSpec(
        rel_dir="sequence_structure/coiled_coil",
        filename="parallel-dimeric-coiled-coil.yaml",
        identifier="proteintraitsmech:COILED_COIL_PARALLEL_DIMER",
        label="parallel dimeric coiled coil",
        definition=(
            "A two-stranded alpha-helical coiled coil in which both chains run N-to-C in the "
            "same orientation, packing a-to-a' and d-to-d' core layers in register."
        ),
        trait_axis="SEQUENCE_STRUCTURE",
        trait_category="MIXED_COILED_COIL",
        parent_traits=("proteintraitsmech:COILED_COIL_HEPTAD_REPEAT",),
        synonyms=(
            ("two-stranded parallel coiled coil", "EXACT_SYNONYM"),
            ("parallel coiled-coil dimer", "EXACT_SYNONYM"),
        ),
        evidence=(("PMID:28118746", "Structural determinants of parallel vs antiparallel dimeric coiled coils."),),
        detection_methods=(M_DEEPCOIL, M_SOCKET),
    ),
    TraitSpec(
        rel_dir="sequence_structure/coiled_coil",
        filename="antiparallel-dimeric-coiled-coil.yaml",
        identifier="proteintraitsmech:COILED_COIL_ANTIPARALLEL_DIMER",
        label="antiparallel dimeric coiled coil",
        definition=(
            "A two-stranded alpha-helical coiled coil in which the constituent helices run "
            "in opposite N-to-C orientations, forming mixed a-d' / d-a' core knobs-into-holes "
            "layers and e-e' / g-g' flanking electrostatic pairs."
        ),
        trait_axis="SEQUENCE_STRUCTURE",
        trait_category="MIXED_COILED_COIL",
        parent_traits=("proteintraitsmech:COILED_COIL_HEPTAD_REPEAT",),
        synonyms=(
            ("two-stranded antiparallel coiled coil", "EXACT_SYNONYM"),
            ("antiparallel coiled-coil hairpin/dimer", "RELATED_SYNONYM"),
        ),
        evidence=(("PMID:28118746", "Packing geometry and electrostatic rules of antiparallel dimeric coiled coils."),),
        detection_methods=(M_DEEPCOIL, M_SOCKET),
    ),
    TraitSpec(
        rel_dir="sequence_structure/coiled_coil",
        filename="trimeric-coiled-coil-bundle.yaml",
        identifier="proteintraitsmech:COILED_COIL_TRIMER",
        label="trimeric coiled-coil bundle",
        definition=(
            "A three-stranded supercoiled alpha-helical bundle (often enriched in isoleucine "
            "or beta-branched residues at both a and d heptad positions), characteristic of "
            "viral class I fusion glycoproteins, collectins, and trimeric autotransporters."
        ),
        trait_axis="SEQUENCE_STRUCTURE",
        trait_category="MIXED_COILED_COIL",
        parent_traits=("proteintraitsmech:COILED_COIL_HEPTAD_REPEAT",),
        synonyms=(
            ("three-stranded coiled coil", "EXACT_SYNONYM"),
            ("coiled-coil trimer", "EXACT_SYNONYM"),
        ),
        evidence=(("PMID:28118746", "Oligomeric state specification in three-stranded coiled-coil bundles."),),
        detection_methods=(M_DEEPCOIL, M_SOCKET),
    ),
    TraitSpec(
        rel_dir="sequence_structure/coiled_coil",
        filename="tetrameric-coiled-coil-bundle.yaml",
        identifier="proteintraitsmech:COILED_COIL_TETRAMER",
        label="tetrameric coiled-coil bundle",
        definition=(
            "A four-stranded parallel or antiparallel supercoiled alpha-helical bundle "
            "(such as SNARE core complexes and LacI tetramerization domains) stabilized by "
            "perpendicular/acute knobs-into-holes packing around a central four-helix core."
        ),
        trait_axis="SEQUENCE_STRUCTURE",
        trait_category="MIXED_COILED_COIL",
        parent_traits=("proteintraitsmech:COILED_COIL_HEPTAD_REPEAT",),
        synonyms=(
            ("four-stranded coiled coil", "EXACT_SYNONYM"),
            ("four-helix coiled-coil bundle", "EXACT_SYNONYM"),
        ),
        evidence=(("PMID:28118746", "Core packing rules for four-helix tetrameric coiled coils."),),
        detection_methods=(M_DEEPCOIL, M_SOCKET),
    ),
    TraitSpec(
        rel_dir="sequence_structure/coiled_coil",
        filename="leucine-zipper-coiled-coil.yaml",
        identifier="proteintraitsmech:COILED_COIL_LEUCINE_ZIPPER",
        label="leucine-zipper coiled coil",
        definition=(
            "A parallel dimeric coiled-coil motif characterized by conserved L-leucine "
            "residues at every seventh (d) position of the heptad repeat and a buried polar "
            "asparagine at an central a position that specifies dimer register."
        ),
        trait_axis="SEQUENCE_STRUCTURE",
        trait_category="MIXED_COILED_COIL",
        parent_traits=("proteintraitsmech:COILED_COIL_PARALLEL_DIMER",),
        synonyms=(
            ("leucine zipper", "EXACT_SYNONYM"),
            ("bZIP leucine-zipper dimerization region", "NARROW_SYNONYM"),
        ),
        xrefs=("SO:0001135",),
        sequence_pattern="L[A-Z]{6}L[A-Z]{6}L[A-Z]{6}L",
        evidence=(("PMID:28118746", "GCN4 and bZIP leucine-zipper coiled-coil dimerization determinants."),),
        detection_methods=(M_DEEPCOIL, M_SOCKET),
    ),
    TraitSpec(
        rel_dir="sequence_structure/coiled_coil",
        filename="hendecad-11-residue-repeat-coiled-coil.yaml",
        identifier="proteintraitsmech:COILED_COIL_HENDECAD_REPEAT",
        label="hendecad (11-residue repeat) coiled coil",
        definition=(
            "A non-canonical coiled-coil segment with an 11-residue (abcdefghijk) sequence "
            "periodicity spanning three helical turns (11/3 = 3.67 residues/turn), producing "
            "a nearly straight, right-handed or untwisted alpha-helical bundle."
        ),
        trait_axis="SEQUENCE_STRUCTURE",
        trait_category="MIXED_COILED_COIL",
        parent_traits=("proteintraitsmech:COILED_COIL",),
        synonyms=(
            ("11/3 coiled-coil repeat", "EXACT_SYNONYM"),
            ("hendecad coiled coil", "EXACT_SYNONYM"),
        ),
        evidence=(("PMID:28118746", "Hendecad (11-mer) and pentadecad (15-mer) non-heptad coiled coils."),),
        detection_methods=(M_DEEPCOIL, M_SOCKET),
    ),
    # --- 8a. Sparse Category Expansion: SEQ_SIGNAL_PEPTIDE (5 records) ---
    TraitSpec(
        rel_dir="sequence/signal_peptide",
        filename="sec-spi-cleavable-signal-peptide.yaml",
        identifier="proteintraitsmech:SIGNAL_PEPTIDE_SEC_SPI",
        label="Sec/SPI cleavable secretory signal peptide",
        definition=(
            "Canonical tripartite N-terminal secretory signal peptide (positively charged "
            "n-region, hydrophobic h-region, and polar c-region with an Ala-X-Ala motif) "
            "translocated across the SecYEG/Sec61 channel and cleaved by signal peptidase I (LepB/SPase I)."
        ),
        trait_axis="SEQUENCE",
        trait_category="SEQ_SIGNAL_PEPTIDE",
        parent_traits=("proteintraitsmech:UNIPROT_FT_SIGNAL",),
        synonyms=(
            ("Sec/SPI signal peptide", "EXACT_SYNONYM"),
            ("type I signal peptidase secretory leader", "EXACT_SYNONYM"),
        ),
        xrefs=("SO:0000418",),
        evidence=(("PMID:34980915", "SignalP 6.0 predicts all five types of signal peptides across bacteria, archaea, and eukarya."),),
        detection_methods=(M_SIGNALP6,),
    ),
    TraitSpec(
        rel_dir="sequence/signal_peptide",
        filename="sec-spii-lipoprotein-signal-peptide.yaml",
        identifier="proteintraitsmech:SIGNAL_PEPTIDE_SEC_SPII",
        label="Sec/SPII lipoprotein signal peptide (lipobox)",
        definition=(
            "Prokaryotic N-terminal secretory signal peptide bearing a conserved C-terminal "
            "lipobox motif ([LVI][ASTVI][GAS]C) whose invariant +1 cysteine is S-diacylglyceryl "
            "modified by Lgt prior to cleavage by lipoprotein signal peptidase II (LspA)."
        ),
        trait_axis="SEQUENCE",
        trait_category="SEQ_SIGNAL_PEPTIDE",
        parent_traits=("proteintraitsmech:UNIPROT_FT_SIGNAL",),
        synonyms=(
            ("Sec/SPII signal peptide", "EXACT_SYNONYM"),
            ("bacterial lipoprotein lipobox signal peptide", "EXACT_SYNONYM"),
        ),
        sequence_pattern="[LVI][ASTVI][GAS]C",
        evidence=(("PMID:34980915", "Discrimination of Sec/SPII lipoprotein lipobox signal peptides by SignalP 6.0."),),
        detection_methods=(M_SIGNALP6,),
    ),
    TraitSpec(
        rel_dir="sequence/signal_peptide",
        filename="tat-spi-twin-arginine-signal-peptide.yaml",
        identifier="proteintraitsmech:SIGNAL_PEPTIDE_TAT_SPI",
        label="Tat/SPI twin-arginine signal peptide",
        definition=(
            "N-terminal signal peptide containing a conserved twin-arginine motif "
            "([ST]RRxFLK) in its n/h boundary that directs folded, cofactor-bound proteins "
            "across the twin-arginine translocation (TatABC) pathway and is cleaved by signal peptidase I."
        ),
        trait_axis="SEQUENCE",
        trait_category="SEQ_SIGNAL_PEPTIDE",
        parent_traits=("proteintraitsmech:UNIPROT_FT_SIGNAL",),
        synonyms=(
            ("Tat/SPI signal peptide", "EXACT_SYNONYM"),
            ("twin-arginine translocation signal peptide", "EXACT_SYNONYM"),
        ),
        sequence_pattern="[ST]RR[A-Z][FLV][LK]",
        evidence=(("PMID:34980915", "Prediction of Tat/SPI twin-arginine signal peptides with SignalP 6.0."),),
        detection_methods=(M_SIGNALP6,),
    ),
    TraitSpec(
        rel_dir="sequence/signal_peptide",
        filename="tat-spii-twin-arginine-lipoprotein-signal-peptide.yaml",
        identifier="proteintraitsmech:SIGNAL_PEPTIDE_TAT_SPII",
        label="Tat/SPII twin-arginine lipoprotein signal peptide",
        definition=(
            "Prokaryotic N-terminal signal peptide combining an n-region twin-arginine (RR) "
            "motif for folded export via the Tat translocon with a c-region lipobox cysteine "
            "processed by lipoprotein signal peptidase II (LspA)."
        ),
        trait_axis="SEQUENCE",
        trait_category="SEQ_SIGNAL_PEPTIDE",
        parent_traits=("proteintraitsmech:UNIPROT_FT_SIGNAL",),
        synonyms=(
            ("Tat/SPII signal peptide", "EXACT_SYNONYM"),
            ("Tat lipoprotein signal peptide", "EXACT_SYNONYM"),
        ),
        evidence=(("PMID:34980915", "Identification of Tat/SPII twin-arginine lipoprotein signal peptides by SignalP 6.0."),),
        detection_methods=(M_SIGNALP6,),
    ),
    TraitSpec(
        rel_dir="sequence/signal_peptide",
        filename="sec-spiii-prepilin-signal-peptide.yaml",
        identifier="proteintraitsmech:SIGNAL_PEPTIDE_SEC_SPIII",
        label="Sec/SPIII type IV prepilin signal peptide",
        definition=(
            "Short basic N-terminal leader peptide of bacterial type IV pilins, pseudopilins, "
            "and archaeal archaellins, cleaved between a conserved glycine (-1) and a hydrophobic "
            "helix (+1 Phe/Met) by prepilin peptidase (PilD / SPase III)."
        ),
        trait_axis="SEQUENCE",
        trait_category="SEQ_SIGNAL_PEPTIDE",
        parent_traits=("proteintraitsmech:UNIPROT_FT_SIGNAL",),
        synonyms=(
            ("Sec/SPIII signal peptide", "EXACT_SYNONYM"),
            ("type IV prepilin leader peptide", "EXACT_SYNONYM"),
        ),
        evidence=(("PMID:34980915", "Sec/SPIII prepilin signal peptide prediction in SignalP 6.0."),),
        detection_methods=(M_SIGNALP6,),
    ),
    # --- 8b. Sparse Category Expansion: SEQ_TRANSIT_PEPTIDE (3 records) ---
    TraitSpec(
        rel_dir="sequence/transit_peptide",
        filename="mitochondrial-matrix-targeting-transit-peptide.yaml",
        identifier="proteintraitsmech:TRANSIT_PEPTIDE_MITOCHONDRIAL",
        label="mitochondrial targeting transit peptide (mTP)",
        definition=(
            "Cleavable N-terminal presequence enriched in positively charged, hydroxylated, "
            "and hydrophobic residues (forming an amphipathic alpha-helix devoid of acidic "
            "residues) recognized by TOM20/TOM22 and cleaved by mitochondrial processing peptidase (MPP)."
        ),
        trait_axis="SEQUENCE",
        trait_category="SEQ_TRANSIT_PEPTIDE",
        parent_traits=("proteintraitsmech:UNIPROT_FT_TRANSIT",),
        synonyms=(
            ("mTP", "EXACT_SYNONYM"),
            ("mitochondrial presequence", "EXACT_SYNONYM"),
            ("mitochondrial matrix targeting signal", "EXACT_SYNONYM"),
        ),
        xrefs=("SO:0001073",),
        evidence=(("PMID:31609389", "TargetP 2.0 predicts mitochondrial, chloroplast, and thylakoid luminal transit peptides."),),
        detection_methods=(M_TARGETP2,),
    ),
    TraitSpec(
        rel_dir="sequence/transit_peptide",
        filename="chloroplast-stroma-transit-peptide.yaml",
        identifier="proteintraitsmech:TRANSIT_PEPTIDE_CHLOROPLAST_STROMA",
        label="chloroplast stroma transit peptide (cTP)",
        definition=(
            "Cleavable N-terminal plastid-targeting sequence enriched in serine/threonine "
            "residues and lacking acidic residues, directing nuclear-encoded precursor proteins "
            "through the TOC/TIC translocons into the chloroplast stroma where SPP cleaves it."
        ),
        trait_axis="SEQUENCE",
        trait_category="SEQ_TRANSIT_PEPTIDE",
        parent_traits=("proteintraitsmech:UNIPROT_FT_TRANSIT",),
        synonyms=(
            ("cTP", "EXACT_SYNONYM"),
            ("chloroplast transit peptide", "EXACT_SYNONYM"),
            ("plastid targeting peptide", "BROAD_SYNONYM"),
        ),
        xrefs=("SO:0001074",),
        evidence=(("PMID:31609389", "TargetP 2.0 discriminates stromal chloroplast transit peptides (cTP) and cleavage sites."),),
        detection_methods=(M_TARGETP2,),
    ),
    TraitSpec(
        rel_dir="sequence/transit_peptide",
        filename="thylakoid-lumen-bipartite-transit-peptide.yaml",
        identifier="proteintraitsmech:TRANSIT_PEPTIDE_THYLAKOID_LUMEN",
        label="thylakoid lumen bipartite transit peptide (luTP)",
        definition=(
            "Bipartite N-terminal plastid transit peptide consisting of an N-terminal stromal "
            "import domain (cTP) followed by a Sec- or Tat-type thylakoid transfer peptide "
            "cleaved by thylakoidal processing peptidase (TPP) in the thylakoid lumen."
        ),
        trait_axis="SEQUENCE",
        trait_category="SEQ_TRANSIT_PEPTIDE",
        parent_traits=("proteintraitsmech:UNIPROT_FT_TRANSIT",),
        synonyms=(
            ("luTP", "EXACT_SYNONYM"),
            ("thylakoid luminal transit peptide", "EXACT_SYNONYM"),
        ),
        xrefs=("SO:0001074",),
        evidence=(("PMID:31609389", "TargetP 2.0 identifies bipartite thylakoid luminal transit peptides (luTP)."),),
        detection_methods=(M_TARGETP2,),
    ),
    # --- 8c. Sparse Category Expansion: SEQ_PROPEPTIDE (3 records) ---
    TraitSpec(
        rel_dir="sequence/propeptide",
        filename="zymogen-activation-inhibitory-propeptide.yaml",
        identifier="proteintraitsmech:PROPEPTIDE_ZYMOGEN_ACTIVATION",
        label="zymogen-activation autoinhibitory propeptide",
        definition=(
            "Cleavable propeptide segment of an enzyme precursor (zymogen) that sterically "
            "blocks or distorts the catalytic cleft (e.g. via a cysteine-switch or activation "
            "peptide) until proteolytic removal triggers irreversible enzyme activation."
        ),
        trait_axis="SEQUENCE",
        trait_category="SEQ_PROPEPTIDE",
        parent_traits=("proteintraitsmech:UNIPROT_FT_PROPEP",),
        synonyms=(
            ("zymogen activation peptide", "EXACT_SYNONYM"),
            ("autoinhibitory pro-domain", "EXACT_SYNONYM"),
        ),
        xrefs=("SO:0001062",),
        evidence=(("PMID:16002793", "Mechanisms of zymogen latency and proteolytic propeptide activation."),),
        detection_methods=(M_PROPEP,),
    ),
    TraitSpec(
        rel_dir="sequence/propeptide",
        filename="intramolecular-chaperone-propeptide.yaml",
        identifier="proteintraitsmech:PROPEPTIDE_INTRAMOLECULAR_CHAPERONE",
        label="intramolecular-chaperone propeptide",
        definition=(
            "Cleavable propeptide domain (exemplified by subtilisin, alpha-lytic protease, "
            "and carboxypeptidase Y pro-regions) that lowers the kinetic folding barrier "
            "of the mature catalytic domain and is subsequently degraded after autocatalytic cleavage."
        ),
        trait_axis="SEQUENCE",
        trait_category="SEQ_PROPEPTIDE",
        parent_traits=("proteintraitsmech:UNIPROT_FT_PROPEP",),
        synonyms=(
            ("IMC propeptide", "EXACT_SYNONYM"),
            ("folding-chaperone prodomain", "EXACT_SYNONYM"),
        ),
        xrefs=("SO:0001062",),
        evidence=(("PMID:16002793", "Intramolecular chaperone propeptides catalyze folding of their cognate protease domains."),),
        detection_methods=(M_PROPEP,),
    ),
    TraitSpec(
        rel_dir="sequence/propeptide",
        filename="prohormone-convertase-dibasic-cleavage-propeptide.yaml",
        identifier="proteintraitsmech:PROPEPTIDE_PROHORMONE_DIBASIC",
        label="prohormone-convertase dibasic-cleavage propeptide",
        definition=(
            "Propeptide segment of a neuroendocrine or growth-factor precursor flanked by "
            "paired basic (KR, RR, or RxxR) proprotein convertase / furin cleavage sites, "
            "excised during secretory granule maturation."
        ),
        trait_axis="SEQUENCE",
        trait_category="SEQ_PROPEPTIDE",
        parent_traits=("proteintraitsmech:UNIPROT_FT_PROPEP",),
        synonyms=(
            ("furin/prohormone convertase propeptide", "EXACT_SYNONYM"),
            ("proprotein convertase pro-region", "EXACT_SYNONYM"),
        ),
        xrefs=("SO:0001062",),
        sequence_pattern="[KR]R|[RK][A-Z]{2}R",
        evidence=(("PMID:22931919", "Biochemistry and substrate specificity of proprotein convertases and dibasic propeptides."),),
        detection_methods=(M_PROPEP,),
    ),
    # --- 8d. Sparse Category Expansion: STRUCT_DISULFIDE (4 records) ---
    TraitSpec(
        rel_dir="structure/disulfide",
        filename="intrachain-structural-disulfide-bond.yaml",
        identifier="proteintraitsmech:DISULFIDE_INTRACHAIN",
        label="intrachain structural disulfide bond",
        definition=(
            "Covalent cystine crosslink formed between two cysteine thiolates within the "
            "same polypeptide chain, reducing unfolded-state chain entropy and stabilizing "
            "tertiary fold topology."
        ),
        trait_axis="STRUCTURE",
        trait_category="STRUCT_DISULFIDE",
        parent_traits=("proteintraitsmech:DISULFIDE_BOND",),
        synonyms=(
            ("intramolecular disulfide bridge", "EXACT_SYNONYM"),
            ("intrachain cystine bridge", "EXACT_SYNONYM"),
        ),
        evidence=(("PMID:17001100", "Structural classification and energetic roles of intrachain vs interchain disulfide bonds."),),
        detection_methods=(M_DSSP_SSBOND,),
    ),
    TraitSpec(
        rel_dir="structure/disulfide",
        filename="interchain-quaternary-disulfide-bond.yaml",
        identifier="proteintraitsmech:DISULFIDE_INTERCHAIN",
        label="interchain quaternary disulfide bond",
        definition=(
            "Covalent cystine crosslink joining cysteine residues on two distinct polypeptide "
            "chains (or mature proteolytically cleaved chains, as in insulin and immunoglobulins), "
            "locking quaternary subunit stoichiometry."
        ),
        trait_axis="STRUCTURE",
        trait_category="STRUCT_DISULFIDE",
        parent_traits=("proteintraitsmech:DISULFIDE_BOND",),
        synonyms=(
            ("intermolecular disulfide bridge", "EXACT_SYNONYM"),
            ("inter-subunit disulfide bond", "EXACT_SYNONYM"),
        ),
        evidence=(("PMID:17001100", "Geometry and quaternary stabilization of interchain disulfide bridges."),),
        detection_methods=(M_DSSP_SSBOND,),
    ),
    TraitSpec(
        rel_dir="structure/disulfide",
        filename="cystine-knot-disulfide-motif.yaml",
        identifier="proteintraitsmech:DISULFIDE_CYSTINE_KNOT",
        label="cystine-knot three-disulfide topology",
        definition=(
            "Topological disulfide motif of three conserved cystine bridges (CysI-CysIV, "
            "CysII-CysV, CysIII-CysVI) in which the third disulfide bond threads through "
            "the macrocycle formed by the first two, conferring extreme thermal and proteolytic stability."
        ),
        trait_axis="STRUCTURE",
        trait_category="STRUCT_DISULFIDE",
        parent_traits=("proteintraitsmech:DISULFIDE_INTRACHAIN",),
        synonyms=(
            ("inhibitor cystine knot", "NARROW_SYNONYM"),
            ("ICK / knottin disulfide topology", "RELATED_SYNONYM"),
            ("cyclic cystine knot", "NARROW_SYNONYM"),
        ),
        evidence=(("PMID:19569188", "Cystine-knot topologies in knottins, cyclotides, and growth factors."),),
        detection_methods=(M_DSSP_SSBOND,),
    ),
    TraitSpec(
        rel_dir="structure/disulfide",
        filename="allosteric-redox-switch-disulfide-bond.yaml",
        identifier="proteintraitsmech:DISULFIDE_ALLOSTERIC_REDOX_SWITCH",
        label="allosteric/catalytic redox-switch disulfide bond",
        definition=(
            "Reversibly cleaved disulfide bond (characteristically adopting a high-strain "
            "-RHStaple, +/-RHHook, or -LHHook dihedral configuration) whose thiol-disulfide "
            "exchange regulates protein conformation or directly mediates dithiol-disulfide catalysis."
        ),
        trait_axis="STRUCTURE",
        trait_category="STRUCT_DISULFIDE",
        parent_traits=("proteintraitsmech:DISULFIDE_BOND",),
        synonyms=(
            ("allosteric disulfide bond", "EXACT_SYNONYM"),
            ("redox-active disulfide switch", "EXACT_SYNONYM"),
        ),
        evidence=(
            ("PMID:17001100", "Allosteric disulfide bonds and their characteristic -RHStaple dihedral geometry."),
            ("PMID:24743683", "Classification of catalytic and allosteric disulfides from dihedral strain energy."),
        ),
        detection_methods=(M_DSSP_SSBOND,),
    ),
    # --- 9. Cross-Mech Missing GO Complex: GO:7770085 (1 record) ---
    TraitSpec(
        rel_dir="function/localization/go",
        filename="protocatechuate-3-4-dioxygenase-complex-go7770085.yaml",
        identifier="GO:7770085",
        label="protocatechuate 3,4-dioxygenase complex",
        definition=(
            "A heterooligomeric non-heme iron dioxygenase enzyme complex composed of alpha "
            "(PcaG) and beta (PcaH) protomers (forming (alpha-beta)n assemblies with a catalytic "
            "Fe(III) site in the beta subunit) that catalyzes the intradiol ortho-cleavage of "
            "protocatechuate (3,4-dihydroxybenzoate) to 3-carboxy-cis,cis-muconate in the "
            "beta-ketoadipate pathway."
        ),
        trait_axis="FUNCTION",
        trait_category="FUNC_LOCALIZATION",
        parent_traits=("GO:1902494",),
        synonyms=(
            ("PcaGH dioxygenase complex", "EXACT_SYNONYM"),
            ("3,4-PCD complex", "EXACT_SYNONYM"),
            ("protocatechuate 3,4-dioxygenase alpha-beta heterooligomer", "EXACT_SYNONYM"),
        ),
        xrefs=("EC:1.13.11.3", "GO:0018578", "RHEA:15457"),
        evidence=(("PMID:2563464", "Crystal structure of protocatechuate 3,4-dioxygenase from Pseudomonas aeruginosa."),),
        detection_methods=(M_GO_COMPLEX,),
        definition_source="GO / CellStructureMech cross-Mech alignment",
    ),
)


def emit_record(spec: TraitSpec) -> str:
    lines: list[str] = [
        f"identifier: {spec.identifier}",
        f"label: {yaml_escape(spec.label)}",
    ]
    f = folded(spec.definition)
    lines.append(f"definition: {f[0]}")
    lines.extend(f[1:])
    lines.append(f"definition_source: {yaml_escape(spec.definition_source)}")
    lines.append(f"trait_axis: {spec.trait_axis}")
    lines.append(f"trait_category: {spec.trait_category}")
    lines.append("term_kind: CLASS")
    lines.append("mapping_status: SEEDED")
    if spec.parent_traits:
        lines.append("parent_traits:")
        for p in spec.parent_traits:
            lines.append(f"  - {p}")
    if spec.synonyms:
        lines.append("synonyms:")
        for syn_text, syn_type in spec.synonyms:
            lines.append(f"  - synonym_text: {yaml_escape(syn_text)}")
            lines.append(f"    synonym_type: {syn_type}")
    if spec.xrefs:
        lines.append("xrefs:")
        for x in spec.xrefs:
            lines.append(f"  - {x}")
    if spec.sequence_pattern:
        lines.append(f"sequence_pattern: {yaml_escape(spec.sequence_pattern)}")
    if spec.detection_methods:
        lines.append("detection_methods:")
        for m in spec.detection_methods:
            lines.append(f"  - name: {yaml_escape(m.name)}")
            lines.append(f"    method_type: {m.method_type}")
            lines.append(f"    edam_operation: {m.edam_operation}")
            lines.append(f"    tool: {yaml_escape(m.tool)}")
            lines.append(f"    evidence_code: {m.evidence_code}")
            lines.append(f"    reference: {m.reference}")
            lines.append(f"    recipe: {yaml_escape(m.recipe)}")
    if spec.evidence:
        lines.append("evidence:")
        for ref, notes in spec.evidence:
            lines.append(f"  - reference: {ref}")
            lines.append(f"    notes: {yaml_escape(notes)}")
    lines.append(f"license: {LICENSE}")
    return "\n".join(lines) + "\n"


def go_0016937_seed() -> tuple[Path, str]:
    """Return path and seed payload to merge obsolete GO:0004085 into GO:0016937."""
    path = (
        TRAITS_DIR
        / "function"
        / "molecular_function"
        / "go"
        / "short-chain-fatty-acyl-coa-dehydrogenase-activity-go0016937.yaml"
    )
    text = """identifier: GO:0016937
label: "short-chain fatty acyl-CoA dehydrogenase activity"
definition: >-
  Catalysis of the reaction: a short-chain 2,3-saturated fatty acyl-CoA + H+ + oxidized [electron-transfer flavoprotein] = a short-chain (2E)-enoyl-CoA + reduced [electron-transfer flavoprotein]. A short-chain fatty acid has an aliphatic tail containing fewer than 6 carbons.
definition_source: "GO (2026-06-15)"
trait_axis: FUNCTION
trait_category: FUNC_MOLECULAR_FUNCTION
term_kind: CLASS
mapping_status: SEEDED
parent_traits:
  - GO:0003995
synonyms:
  - synonym_text: "butanoyl-CoA dehydrogenase"
    synonym_type: NARROW_SYNONYM
  - synonym_text: "butyryl dehydrogenase"
    synonym_type: NARROW_SYNONYM
  - synonym_text: "butyryl-CoA dehydrogenase activity"
    synonym_type: EXACT_SYNONYM
  - synonym_text: "short-chain acyl CoA dehydrogenase"
    synonym_type: EXACT_SYNONYM
  - synonym_text: "short-chain-acyl-CoA dehydrogenase activity"
    synonym_type: EXACT_SYNONYM
  - synonym_text: "unsaturated acyl-CoA reductase"
    synonym_type: BROAD_SYNONYM
xrefs:
  - EC:1.3.8.1
  - GO:0004085
  - KEGG_REACTION:R01178
  - MetaCyc:RXN-13449
  - RHEA:24004
  - RHEA:31287
  - RHEA:43456
  - RHEA:47196
  - UM-BBD_reactionID:r0013
license: CC-BY 4.0
"""
    return path, text


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="write YAMLs (default: dry-run)")
    ap.add_argument("--force", action="store_true", help="re-merge existing files")
    args = ap.parse_args()

    written = skipped = 0
    for spec in SPECS:
        path = TRAITS_DIR / spec.rel_dir / spec.filename
        if path.exists() and not args.force:
            skipped += 1
            continue
        if args.apply:
            path.parent.mkdir(parents=True, exist_ok=True)
            write_record(path, emit_record(spec), validate=True)
            written += 1

    # Also merge GO:0004085 alt_id into existing GO:0016937 record if not already present.
    go_path, go_seed = go_0016937_seed()
    go_updated = False
    if go_path.exists():
        existing_go = go_path.read_text(encoding="utf-8")
        if "GO:0004085" not in existing_go or args.force:
            go_updated = True
            if args.apply:
                write_record(go_path, go_seed, validate=True)

    print(f"{len(SPECS)} foundational protein-trait records defined across 12 categories.")
    if args.apply:
        print(f"Wrote {written}; skipped {skipped} existing; GO:0016937 alt_id merged={go_updated}.")
    else:
        print(
            f"Dry-run — would write {len(SPECS) - skipped} new records "
            f"({skipped} already exist); GO:0016937 alt_id merge pending={go_updated}. "
            f"Re-run with --apply."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
