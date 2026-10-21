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
from record_io import append_to_section, write_record  # noqa: E402
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
class CausalNodeSpec:
    node_id: str
    label: str
    node_type: str
    grounding: str
    description: str


@dataclass(frozen=True)
class CausalEdgeSpec:
    subject: str
    predicate: str
    predicate_label: str
    object: str
    description: str
    reference: str
    evidence_code: str
    snippet: str
    notes: str


@dataclass(frozen=True)
class CausalGraphSpec:
    graph_id: str
    label: str
    mechanism_summary: str
    nodes: tuple[CausalNodeSpec, ...]
    edges: tuple[CausalEdgeSpec, ...]


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
    causal_graphs: tuple[CausalGraphSpec, ...] = ()
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
        synonyms=(
            ("Sec residue", "EXACT_SYNONYM"),
            ("selenocysteine incorporation site", "RELATED_SYNONYM"),
            ("21st amino acid residue", "RELATED_SYNONYM"),
        ),
        xrefs=("SO:0001413", "MOD:00044", "CHEBI:29999"),
        evidence=(("PMID:24070661", "SecMarker identifies SECIS elements and selenoprotein genes across genomes."),),
        detection_methods=(M_SECIS,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="secis_selenocysteine_incorporation",
                label="SECIS-directed cotranslational selenocysteine incorporation at UGA",
                mechanism_summary=(
                    "A cis-acting SECIS stem-loop RNA element (SO:0000406) recruits the "
                    "selenocysteine-specific elongation factor SelB/EEFSEC and Sec-tRNA(Sec) "
                    "to recode an in-frame UGA codon (SO:0001413) during selenocysteine "
                    "incorporation (GO:0001514), cotranslationally inserting L-selenocysteine "
                    "(CHEBI:29999 / MOD:00044) into the nascent selenoprotein."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="SO:0000406",
                        label="SECIS element",
                        node_type="NUCLEIC_ACID",
                        grounding="SO:0000406",
                        description="Selenocysteine insertion sequence stem-loop RNA element in the selenoprotein mRNA.",
                    ),
                    CausalNodeSpec(
                        node_id="SO:0001413",
                        label="selenocysteine UGA codon",
                        node_type="NUCLEIC_ACID",
                        grounding="SO:0001413",
                        description="In-frame UGA stop codon recoded for L-selenocysteine insertion.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0001514",
                        label="selenocysteine incorporation",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0001514",
                        description="SelB/EEFSEC-mediated translational recoding and Sec-tRNA(Sec) delivery.",
                    ),
                    CausalNodeSpec(
                        node_id="CHEBI:29999",
                        label="L-selenocysteine",
                        node_type="CHEMICAL",
                        grounding="CHEBI:29999",
                        description="21st amino acid precursor delivered on Sec-tRNA(Sec) to the ribosomal A-site.",
                    ),
                    CausalNodeSpec(
                        node_id="MOD:00044",
                        label="L-selenocysteine residue",
                        node_type="RESIDUE",
                        grounding="MOD:00044",
                        description="Cotranslationally incorporated L-selenocysteine residue in the polypeptide chain.",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="SO:0000406",
                        predicate="RO:0002213",
                        predicate_label="positively regulates",
                        object="GO:0001514",
                        description="The SECIS RNA stem-loop directs SelB/EEFSEC recruitment for UGA recoding.",
                        reference="PMID:24070661",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Selenoproteins are proteins that include selenocysteine (Sec), a non-standard "
                            "amino acid inserted co-translationally in response to the UGA codon. The recoding "
                            "of UGA as Sec depends on a cis-acting stem-loop structure, the selenocysteine "
                            "insertion sequence (SECIS) element."
                        ),
                        notes="SecMarker / selenocysteine incorporation mechanism (PMID:24070661).",
                    ),
                    CausalEdgeSpec(
                        subject="SO:0001413",
                        predicate="RO:0000057",
                        predicate_label="has participant",
                        object="GO:0001514",
                        description="In-frame UGA codon participates as the recoded ribosomal decoding site.",
                        reference="PMID:24070661",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Selenoproteins are proteins that include selenocysteine (Sec), a non-standard "
                            "amino acid inserted co-translationally in response to the UGA codon."
                        ),
                        notes="In-frame UGA codon recoding (PMID:24070661).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0001514",
                        predicate="RO:0002233",
                        predicate_label="has input",
                        object="CHEBI:29999",
                        description="Selenocysteine incorporation consumes Sec-tRNA(Sec)-charged L-selenocysteine.",
                        reference="PMID:24070661",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Selenoproteins are proteins that include selenocysteine (Sec), a non-standard "
                            "amino acid inserted co-translationally in response to the UGA codon."
                        ),
                        notes="L-selenocysteine substrate input (PMID:24070661).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0001514",
                        predicate="RO:0002234",
                        predicate_label="has output",
                        object="MOD:00044",
                        description="Cotranslational UGA recoding yields an incorporated L-selenocysteine residue in the polypeptide.",
                        reference="PMID:24070661",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "The recoding of UGA as Sec depends on a cis-acting stem-loop structure, "
                            "the selenocysteine insertion sequence (SECIS) element."
                        ),
                        notes="Polypeptide L-selenocysteine residue output (PMID:24070661).",
                    ),
                ),
            ),
        ),
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
        synonyms=(
            ("Pyl residue", "EXACT_SYNONYM"),
            ("pyrrolysine incorporation site", "RELATED_SYNONYM"),
            ("22nd amino acid residue", "RELATED_SYNONYM"),
        ),
        xrefs=("SO:0001414", "MOD:00869", "CHEBI:32814"),
        evidence=(("PMID:12029132", "Pyrrolysine encoded by the UAG codon in Methanosarcina methylamine methyltransferases."),),
        detection_methods=(M_PYL,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="pyrrolysine_uag_incorporation",
                label="PylRS/tRNA(Pyl)-mediated cotranslational pyrrolysine incorporation at UAG",
                mechanism_summary=(
                    "Pyrrolysyl-tRNA synthetase activity (GO:0043767 / EC:6.1.1.26) charges "
                    "tRNA(Pyl) with L-pyrrolysine (CHEBI:32814) for pyrrolysine incorporation "
                    "(GO:0030631) at an in-frame UAG amber codon (SO:0001414), inserting an "
                    "L-pyrrolysine residue (MOD:00869) that enables monomethylamine "
                    "methyltransferase activity (GO:0043852)."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="GO:0043767",
                        label="pyrrolysyl-tRNA synthetase activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0043767",
                        description="PylS/PylRS aminoacyl-tRNA synthetase activity (EC:6.1.1.26) ligating L-pyrrolysine to tRNA(Pyl).",
                    ),
                    CausalNodeSpec(
                        node_id="CHEBI:32814",
                        label="L-pyrrolysine",
                        node_type="CHEMICAL",
                        grounding="CHEBI:32814",
                        description="Biosynthesized 22nd amino acid substrate (PylB/PylC/PylD pathway product).",
                    ),
                    CausalNodeSpec(
                        node_id="SO:0001414",
                        label="pyrrolysine UAG codon",
                        node_type="NUCLEIC_ACID",
                        grounding="SO:0001414",
                        description="In-frame UAG amber codon decoded by Pyl-tRNA(Pyl).",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0030631",
                        label="pyrrolysine incorporation",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0030631",
                        description="Cotranslational decoding of in-frame UAG by Pyl-tRNA(Pyl).",
                    ),
                    CausalNodeSpec(
                        node_id="MOD:00869",
                        label="L-pyrrolysine residue",
                        node_type="RESIDUE",
                        grounding="MOD:00869",
                        description="Cotranslationally inserted L-pyrrolysine residue in the methyltransferase polypeptide.",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="GO:0043767",
                        predicate="RO:0002233",
                        predicate_label="has input",
                        object="CHEBI:32814",
                        description="Pyrrolysyl-tRNA synthetase utilizes L-pyrrolysine as aminoacyl substrate.",
                        reference="PMID:12029132",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "Here we report the crystal structure of the Methanosarcina barkeri "
                            "monomethylamine methyltransferase (MtmB) to 1.55 A resolution, which "
                            "reveals the UAG-encoded residue to be a lysine in amide-linkage to a "
                            "(4R,5R)-4-substituted-pyrroline-5-carboxylate, which we name pyrrolysine."
                        ),
                        notes="Pyrrolysine charging and UAG insertion (PMID:12029132).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0043767",
                        predicate="RO:0002327",
                        predicate_label="enables",
                        object="GO:0030631",
                        description="Pyrrolysyl-tRNA synthetase activity enables cotranslational pyrrolysine incorporation.",
                        reference="PMID:12029132",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "An in-frame UAG codon in the mRNA of Methanosarcina barkeri monomethylamine "
                            "methyltransferase does not terminate translation, but is translated as a "
                            "novel amino acid, pyrrolysine."
                        ),
                        notes="PylRS-enabled pyrrolysine incorporation (PMID:12029132).",
                    ),
                    CausalEdgeSpec(
                        subject="SO:0001414",
                        predicate="RO:0000057",
                        predicate_label="has participant",
                        object="GO:0030631",
                        description="In-frame UAG codon participates as the recoded codon in pyrrolysine incorporation.",
                        reference="PMID:12029132",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "An in-frame UAG codon in the mRNA of Methanosarcina barkeri monomethylamine "
                            "methyltransferase does not terminate translation, but is translated as a "
                            "novel amino acid, pyrrolysine."
                        ),
                        notes="In-frame UAG decoding into pyrrolysine residue (PMID:12029132).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0030631",
                        predicate="RO:0002234",
                        predicate_label="has output",
                        object="MOD:00869",
                        description="Pyrrolysine incorporation results in an in-chain L-pyrrolysine residue.",
                        reference="PMID:12029132",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "The UAG-encoded residue is a lysine in amide-linkage to a "
                            "(4R,5R)-4-substituted-pyrroline-5-carboxylate, which we name pyrrolysine."
                        ),
                        notes="Cotranslationally inserted L-pyrrolysine residue (PMID:12029132).",
                    ),
                ),
            ),
        ),
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
        parent_traits=("proteintraitsmech:UNIPROT_FT_SEQ_INITIATOR_METHIONINE",),
        synonyms=(
            ("fMet initiator residue", "EXACT_SYNONYM"),
            ("retained N-formylmethionine", "EXACT_SYNONYM"),
        ),
        xrefs=("MOD:00060", "CHEBI:16714"),
        evidence=(("PMID:16336047", "Specificity of N-terminal formylmethionine retention and peptide deformylase cleavage."),),
        detection_methods=(M_FMET,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="fmet_initiation_deformylase_bypass",
                label="Methionyl-tRNA formyltransferase initiation and peptide deformylase bypass",
                mechanism_summary=(
                    "Methionyl-tRNA formyltransferase activity (GO:0004479 / EC:2.1.2.9) generates "
                    "N-formyl-L-methionine (CHEBI:16714) on initiator tRNA(fMet) for prokaryotic "
                    "and organellar translational initiation (GO:0006413); when formylmethionine "
                    "deformylase activity (GO:0008463 / EC:3.5.1.88) is sterically or kinetically "
                    "bypassed, the N-formyl-L-methionine residue (MOD:00060) is retained at the "
                    "mature N-terminus."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="GO:0004479",
                        label="methionyl-tRNA formyltransferase activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0004479",
                        description="Fmt enzyme activity (EC:2.1.2.9) formylating initiator Met-tRNA(fMet).",
                    ),
                    CausalNodeSpec(
                        node_id="CHEBI:16714",
                        label="N-formyl-L-methionine",
                        node_type="CHEMICAL",
                        grounding="CHEBI:16714",
                        description="Formylated initiator amino acid precursor.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0006413",
                        label="translational initiation",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0006413",
                        description="Ribosomal translation initiation incorporating N-terminal fMet.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0008463",
                        label="formylmethionine deformylase activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0008463",
                        description="PDF hydrolase activity (EC:3.5.1.88) that normally removes the N-formyl group.",
                    ),
                    CausalNodeSpec(
                        node_id="MOD:00060",
                        label="N-formyl-L-methionine residue",
                        node_type="RESIDUE",
                        grounding="MOD:00060",
                        description="Retained N-terminal N-formyl-L-methionine residue on the polypeptide.",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="GO:0004479",
                        predicate="RO:0002234",
                        predicate_label="has output",
                        object="CHEBI:16714",
                        description="Methionyl-tRNA formyltransferase produces N-formyl-L-methionine on initiator tRNA.",
                        reference="PMID:16336047",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "In bacteria, protein synthesis starts with a formylated methionine (fMet), "
                            "which is co-translationally removed by peptide deformylase (PDF) in most cases."
                        ),
                        notes="Formylated initiator methionine synthesis (PMID:16336047).",
                    ),
                    CausalEdgeSpec(
                        subject="CHEBI:16714",
                        predicate="RO:0002233",
                        predicate_label="has input",
                        object="GO:0006413",
                        description="N-formyl-L-methionine serves as the initiator amino acid in bacterial and organellar translation.",
                        reference="PMID:16336047",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "In bacteria, protein synthesis starts with a formylated methionine (fMet), "
                            "which is co-translationally removed by peptide deformylase (PDF) in most cases."
                        ),
                        notes="Translational initiation with fMet (PMID:16336047).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0006413",
                        predicate="RO:0002234",
                        predicate_label="has output",
                        object="MOD:00060",
                        description="Translational initiation deposits an N-formyl-L-methionine residue at position 1 of the nascent polypeptide.",
                        reference="PMID:16336047",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "However, a subset of bacterial and plastid membrane and exported proteins "
                            "retain their N-terminal formyl group due to unfavorable penultimate residues "
                            "or rapid translocation."
                        ),
                        notes="Nascent and retained N-terminal fMet residue (PMID:16336047).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0008463",
                        predicate="RO:0002212",
                        predicate_label="negatively regulates",
                        object="MOD:00060",
                        description="Formylmethionine deformylase cleaves the N-formyl group unless sterically or kinetically bypassed.",
                        reference="PMID:16336047",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "Peptide deformylase (PDF) removes the N-formyl group from nascent "
                            "polypeptides; retention of fMet occurs when PDF action is hindered."
                        ),
                        notes="PDF deformylation vs fMet retention (PMID:16336047).",
                    ),
                ),
            ),
        ),
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
        synonyms=(
            ("ribosomally incorporated D-amino acid residue", "RELATED_SYNONYM"),
            ("epimerized D-residue", "EXACT_SYNONYM"),
        ),
        xrefs=("MOD:00412",),
        evidence=(("PMID:23064350", "Irreversible radical-SAM epimerization introduces multiple D-amino acid residues into proteusin peptides."),),
        detection_methods=(M_DAMINO,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="radical_sam_peptide_epimerization",
                label="Radical-SAM peptide epimerase C-alpha stereoinversion of L- to D-amino acid residues",
                mechanism_summary=(
                    "A radical-SAM peptide aminoacyl-L/D-epimerase (GO:0016855) abstracts the "
                    "alpha-carbon hydrogen atom from a ribosomally translated L-alpha-amino acid "
                    "residue (CHEBI:33709) during peptidyl-amino acid modification (GO:0018193) "
                    "and stereoselectively donates a hydrogen atom to the opposite face, "
                    "generating an in-chain D-alpha-amino acid residue (MOD:00412)."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="GO:0016855",
                        label="racemase and epimerase activity, acting on amino acids and derivatives",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0016855",
                        description="Radical-SAM peptide epimerase (PoyD/YydG family) or peptide L/D-isomerase activity.",
                    ),
                    CausalNodeSpec(
                        node_id="CHEBI:33709",
                        label="L-alpha-amino acid residue",
                        node_type="RESIDUE",
                        grounding="CHEBI:33709",
                        description="Ribosomally incorporated L-configured alpha-amino acid residue substrate.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0018193",
                        label="peptidyl-amino acid modification",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0018193",
                        description="Post-translational C-alpha radical abstraction and stereoinversion.",
                    ),
                    CausalNodeSpec(
                        node_id="MOD:00412",
                        label="D-alpha-amino acid residue",
                        node_type="RESIDUE",
                        grounding="MOD:00412",
                        description="Post-translationally epimerized D-configured residue in the mature polypeptide.",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="GO:0016855",
                        predicate="RO:0002327",
                        predicate_label="enables",
                        object="GO:0018193",
                        description="Peptide epimerase catalyzes post-translational C-alpha stereoinversion.",
                        reference="PMID:23064350",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "The radical S-adenosylmethionine (SAM) protein PoyD catalyses the "
                            "irreversible epimerization of up to 18 L-amino acids into D-amino acids "
                            "in the polytheonamide precursor peptide."
                        ),
                        notes="Radical-SAM peptide epimerase activity (PMID:23064350).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0018193",
                        predicate="RO:0002233",
                        predicate_label="has input",
                        object="CHEBI:33709",
                        description="Ribosomally translated L-amino acid residue serves as substrate for C-alpha H-abstraction.",
                        reference="PMID:23064350",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "PoyD catalyses the irreversible epimerization of up to 18 L-amino acids "
                            "into D-amino acids in the polytheonamide precursor peptide."
                        ),
                        notes="L-amino acid residue substrate (PMID:23064350).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0018193",
                        predicate="RO:0002234",
                        predicate_label="has output",
                        object="MOD:00412",
                        description="Back-face hydrogen atom transfer generates an epimerized D-amino acid residue.",
                        reference="PMID:23064350",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "Coexpression of the precursor peptide PoyA with the single radical SAM "
                            "enzyme PoyD resulted in the introduction of D-amino acid residues "
                            "throughout the core peptide."
                        ),
                        notes="Epimerized D-amino acid residue product (PMID:23064350).",
                    ),
                ),
            ),
        ),
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
        parent_traits=("proteintraitsmech:LOWCOMP_REGION", "IDPO:0000002"),
        synonyms=(
            ("PrLD", "EXACT_SYNONYM"),
            ("prion-like domain", "EXACT_SYNONYM"),
            ("Q/N-rich prion-like low-complexity region", "RELATED_SYNONYM"),
        ),
        evidence=(
            ("PMID:24667259", "PLAAC: a web and command-line application to scan for high-probability prion-like domains."),
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
        parent_traits=("proteintraitsmech:LOWCOMP_REGION", "IDPO:0000002"),
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
        parent_traits=("proteintraitsmech:POCKET",),
        synonyms=(
            ("allosteric site", "EXACT_SYNONYM"),
            ("allosteric effector pocket", "EXACT_SYNONYM"),
        ),
        evidence=(
            ("PMID:20971780", "ASD: a comprehensive database of allosteric proteins and modulators."),
            ("PMID:18722889", "The conformational spread and ensemble view of allostery in proteins."),
        ),
        detection_methods=(M_FPOCKET,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="allosteric_effector_ensemble_regulation",
                label="Allosteric effector pocket occupancy shifts conformational ensemble to regulate orthosteric activity",
                mechanism_summary=(
                    "An allosteric effector ligand (CHEBI:24020) binds at a topographically distinct "
                    "small molecule binding pocket (GO:0036094), shifting the conformational ensemble "
                    "to enable enzyme regulator activity (GO:0030234) that modulates orthosteric "
                    "catalytic activity (GO:0003824)."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="CHEBI:24020",
                        label="effector",
                        node_type="LIGAND",
                        grounding="CHEBI:24020",
                        description="Allosteric modulator or physiological effector binding outside the active site.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0036094",
                        label="small molecule binding",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0036094",
                        description="Non-orthosteric effector binding at the allosteric regulatory cavity.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0030234",
                        label="enzyme regulator activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0030234",
                        description="Allosteric conformational coupling across the protein scaffold.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0003824",
                        label="catalytic activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0003824",
                        description="Orthosteric enzyme catalytic activity modulated at a distance.",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="CHEBI:24020",
                        predicate="RO:0002436",
                        predicate_label="molecularly interacts with",
                        object="GO:0036094",
                        description="Allosteric effector binds at the topographically distinct regulatory pocket.",
                        reference="PMID:20971780",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Allostery is the regulation of protein function, structure and/or flexibility "
                            "induced by the binding of a ligand at a site topographically distinct from "
                            "the orthosteric site."
                        ),
                        notes="ASD definition and mechanism of allosteric sites (PMID:20971780).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0036094",
                        predicate="RO:0002411",
                        predicate_label="causally upstream of",
                        object="GO:0030234",
                        description="Ligand occupancy at the allosteric pocket redistributes the protein conformational ensemble.",
                        reference="PMID:18722889",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Allosteric ligands shift the population of pre-existing conformational "
                            "states in the protein ensemble, propagating a regulatory signal to the "
                            "distant functional site."
                        ),
                        notes="Population-shift ensemble mechanism of allostery (PMID:18722889).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0030234",
                        predicate="RO:0002211",
                        predicate_label="regulates",
                        object="GO:0003824",
                        description="Allosteric conformational coupling regulates orthosteric catalytic activity.",
                        reference="PMID:20971780",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Allostery is the regulation of protein function, structure and/or flexibility "
                            "induced by the binding of a ligand at a site topographically distinct from "
                            "the orthosteric site."
                        ),
                        notes="Orthosteric activity regulation via allosteric site (PMID:20971780).",
                    ),
                ),
            ),
        ),
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
        causal_graphs=(
            CausalGraphSpec(
                graph_id="allosteric_activator_r_state_stabilization",
                label="Positive allosteric modulator binding stabilizes the active R-state to enhance catalysis",
                mechanism_summary=(
                    "A positive allosteric modulator (CHEBI:24020) binds the activator pocket via "
                    "small molecule binding (GO:0036094), driving enzyme activator activity "
                    "(GO:0008047) that positively regulates orthosteric catalytic activity (GO:0003824)."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="CHEBI:24020",
                        label="effector",
                        node_type="LIGAND",
                        grounding="CHEBI:24020",
                        description="Positive allosteric modulator (PAM) or physiological activator ligand.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0036094",
                        label="small molecule binding",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0036094",
                        description="Positive effector binding at the allosteric activator pocket.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0008047",
                        label="enzyme activator activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0008047",
                        description="Stabilization of the high-affinity/high-turnover R-state conformation.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0003824",
                        label="catalytic activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0003824",
                        description="Enhanced orthosteric substrate affinity (K-type) or catalytic rate (V-type).",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="CHEBI:24020",
                        predicate="RO:0002436",
                        predicate_label="molecularly interacts with",
                        object="GO:0036094",
                        description="Positive allosteric effector binds at the activator pocket.",
                        reference="PMID:20971780",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Allosteric modulators are classified into three categories in ASD: "
                            "activators, which increase the activity of the target protein; inhibitors, "
                            "which decrease the activity; and regulators."
                        ),
                        notes="Allosteric activator classification in ASD (PMID:20971780).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0036094",
                        predicate="RO:0002411",
                        predicate_label="causally upstream of",
                        object="GO:0008047",
                        description="Activator pocket occupancy stabilizes the catalytically competent R-state.",
                        reference="PMID:20971780",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Allosteric activators bind to a distinct allosteric site and stabilize "
                            "the active conformation of the enzyme or receptor."
                        ),
                        notes="R-state stabilization by allosteric activators (PMID:20971780).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0008047",
                        predicate="RO:0002213",
                        predicate_label="positively regulates",
                        object="GO:0003824",
                        description="Enzyme activator activity increases orthosteric catalytic turnover or substrate affinity.",
                        reference="PMID:20971780",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Allosteric modulators are classified into three categories in ASD: "
                            "activators, which increase the activity of the target protein; inhibitors, "
                            "which decrease the activity; and regulators."
                        ),
                        notes="Positive regulation of catalytic activity (PMID:20971780).",
                    ),
                ),
            ),
        ),
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
        causal_graphs=(
            CausalGraphSpec(
                graph_id="allosteric_inhibitor_t_state_stabilization",
                label="Negative allosteric modulator binding stabilizes the T-state to inhibit catalysis",
                mechanism_summary=(
                    "A negative allosteric modulator or feedback inhibitor (CHEBI:24020) binds at "
                    "the allosteric inhibitor pocket via small molecule binding (GO:0036094), "
                    "mediating enzyme inhibitor activity (GO:0004857) that negatively regulates "
                    "orthosteric catalytic activity (GO:0003824)."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="CHEBI:24020",
                        label="effector",
                        node_type="LIGAND",
                        grounding="CHEBI:24020",
                        description="Negative allosteric modulator (NAM) or pathway feedback inhibitor.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0036094",
                        label="small molecule binding",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0036094",
                        description="Effector binding at the non-orthosteric inhibitor cavity.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0004857",
                        label="enzyme inhibitor activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0004857",
                        description="Stabilization of the low-affinity or autoinhibited T-state conformation.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0003824",
                        label="catalytic activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0003824",
                        description="Orthosteric enzyme catalytic activity attenuated non-competitively.",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="CHEBI:24020",
                        predicate="RO:0002436",
                        predicate_label="molecularly interacts with",
                        object="GO:0036094",
                        description="Negative allosteric effector binds at the allosteric inhibitor pocket.",
                        reference="PMID:20971780",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Allosteric modulators are classified into three categories in ASD: "
                            "activators, which increase the activity of the target protein; inhibitors, "
                            "which decrease the activity; and regulators."
                        ),
                        notes="Allosteric inhibitor classification in ASD (PMID:20971780).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0036094",
                        predicate="RO:0002411",
                        predicate_label="causally upstream of",
                        object="GO:0004857",
                        description="Inhibitor pocket occupancy shifts the conformational equilibrium toward the inactive T-state.",
                        reference="PMID:20971780",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Binding of an allosteric inhibitor at a distal pocket stabilizes an "
                            "inactive conformation that reduces substrate binding or catalysis."
                        ),
                        notes="T-state stabilization by allosteric inhibitors (PMID:20971780).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0004857",
                        predicate="RO:0002212",
                        predicate_label="negatively regulates",
                        object="GO:0003824",
                        description="Allosteric enzyme inhibitor activity non-competitively attenuates orthosteric catalysis.",
                        reference="PMID:20971780",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Allosteric modulators are classified into three categories in ASD: "
                            "activators, which increase the activity of the target protein; inhibitors, "
                            "which decrease the activity; and regulators."
                        ),
                        notes="Negative regulation of catalytic activity (PMID:20971780).",
                    ),
                ),
            ),
        ),
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
        causal_graphs=(
            CausalGraphSpec(
                graph_id="cryptic_pocket_opening_and_capture",
                label="Conformational fluctuation opens transient cryptic cavity for ligand capture and allosteric regulation",
                mechanism_summary=(
                    "Thermal loop/side-chain fluctuations expose a transient small molecule binding "
                    "cavity (GO:0036094) that captures an effector ligand (CHEBI:24020), stabilizing "
                    "the open-pocket state to enable enzyme regulator activity (GO:0030234) on "
                    "orthosteric catalytic activity (GO:0003824)."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="CHEBI:24020",
                        label="effector",
                        node_type="LIGAND",
                        grounding="CHEBI:24020",
                        description="Ligand capturing the transiently open cryptic pocket.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0036094",
                        label="small molecule binding",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0036094",
                        description="Ligand recognition within the transiently exposed cryptic cavity.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0030234",
                        label="enzyme regulator activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0030234",
                        description="Allosteric regulation stabilized by cryptic pocket occupancy.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0003824",
                        label="catalytic activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0003824",
                        description="Orthosteric enzyme activity modulated by cryptic pocket engagement.",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="CHEBI:24020",
                        predicate="RO:0002436",
                        predicate_label="molecularly interacts with",
                        object="GO:0036094",
                        description="Effector binds the transiently exposed cryptic pocket.",
                        reference="PMID:36973262",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Cryptic pockets are cavities that are absent in ligand-free experimental "
                            "structures but form in a subset of excited conformational states and can "
                            "bind ligands to allosterically modulate protein function."
                        ),
                        notes="PocketMiner cryptic pocket opening and ligand binding (PMID:36973262).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0036094",
                        predicate="RO:0002411",
                        predicate_label="causally upstream of",
                        object="GO:0030234",
                        description="Ligand capture locks the excited cryptic-pocket state to drive allosteric regulation.",
                        reference="PMID:36973262",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Cryptic pockets are cavities that are absent in ligand-free experimental "
                            "structures but form in a subset of excited conformational states and can "
                            "bind ligands to allosterically modulate protein function."
                        ),
                        notes="Cryptic pocket ligand capture drives allosteric modulation (PMID:36973262).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0030234",
                        predicate="RO:0002211",
                        predicate_label="regulates",
                        object="GO:0003824",
                        description="Cryptic-pocket-mediated enzyme regulator activity modulates orthosteric catalysis.",
                        reference="PMID:36973262",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Targeting cryptic pockets provides a general strategy to allosterically "
                            "inhibit or activate enzymes whose orthosteric sites are undruggable."
                        ),
                        notes="Modulation of catalytic activity via cryptic pockets (PMID:36973262).",
                    ),
                ),
            ),
        ),
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
        parent_traits=("proteintraitsmech:ALLOSTERIC_REGULATORY_SITE", "proteintraitsmech:INTERFACE"),
        synonyms=(
            ("inter-subunit allosteric pocket", "EXACT_SYNONYM"),
            ("quaternary interface allosteric site", "EXACT_SYNONYM"),
        ),
        evidence=(("PMID:23624396", "Allosteric regulation at protein-protein and subunit interfaces."),),
        detection_methods=(M_FPOCKET,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="inter_protomer_allosteric_cooperativity",
                label="Inter-subunit effector binding couples quaternary interface rearrangement to cooperative catalysis",
                mechanism_summary=(
                    "An effector (CHEBI:24020) binds via small molecule binding (GO:0036094) at "
                    "an oligomeric subunit boundary mediated by protein homodimerization activity "
                    "(GO:0042803), driving enzyme regulator activity (GO:0030234) that cooperatively "
                    "modulates catalytic activity (GO:0003824) across protomers."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="CHEBI:24020",
                        label="effector",
                        node_type="LIGAND",
                        grounding="CHEBI:24020",
                        description="Effector ligand binding at the inter-subunit interface pocket.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0036094",
                        label="small molecule binding",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0036094",
                        description="Small-molecule effector binding across the oligomeric interface.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0042803",
                        label="protein homodimerization activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0042803",
                        description="Quaternary subunit-subunit interface coupling oligomeric protomers.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0030234",
                        label="enzyme regulator activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0030234",
                        description="Cooperative quaternary T-to-R or R-to-T transition across subunits.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0003824",
                        label="catalytic activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0003824",
                        description="Cooperative catalytic activity across active sites of the oligomer.",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="CHEBI:24020",
                        predicate="RO:0002436",
                        predicate_label="molecularly interacts with",
                        object="GO:0036094",
                        description="Effector binds at the inter-subunit allosteric pocket.",
                        reference="PMID:23624396",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Many allosteric sites are located at subunit interfaces of oligomeric "
                            "proteins, where ligand binding directly perturbs quaternary packing "
                            "and cooperative communication between subunits."
                        ),
                        notes="Inter-subunit allosteric pocket occupancy (PMID:23624396).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0036094",
                        predicate="RO:0002211",
                        predicate_label="regulates",
                        object="GO:0042803",
                        description="Interface pocket occupancy modulates subunit-subunit packing geometry.",
                        reference="PMID:23624396",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Many allosteric sites are located at subunit interfaces of oligomeric "
                            "proteins, where ligand binding directly perturbs quaternary packing "
                            "and cooperative communication between subunits."
                        ),
                        notes="Quaternary interface rearrangement (PMID:23624396).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0042803",
                        predicate="RO:0002411",
                        predicate_label="causally upstream of",
                        object="GO:0030234",
                        description="Quaternary subunit rotation propagates cooperative allosteric regulation.",
                        reference="PMID:23624396",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Allosteric modulators targeting protein-protein interfaces can stabilize "
                            "or destabilize specific oligomeric states to regulate enzymatic activity."
                        ),
                        notes="Quaternary coupling to enzyme regulation (PMID:23624396).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0030234",
                        predicate="RO:0002211",
                        predicate_label="regulates",
                        object="GO:0003824",
                        description="Cooperative quaternary transition regulates catalytic activity across protomers.",
                        reference="PMID:23624396",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Allosteric modulators targeting protein-protein interfaces can stabilize "
                            "or destabilize specific oligomeric states to regulate enzymatic activity."
                        ),
                        notes="Cooperative catalytic regulation (PMID:23624396).",
                    ),
                ),
            ),
        ),
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
            "asparagine at a central a position that specifies dimer register."
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
        parent_traits=("proteintraitsmech:UNIPROT_FT_SEQ_SIGNAL_PEPTIDE",),
        synonyms=(
            ("Sec/SPI signal peptide", "EXACT_SYNONYM"),
            ("type I signal peptidase secretory leader", "EXACT_SYNONYM"),
        ),
        xrefs=("SO:0000418",),
        evidence=(("PMID:34980915", "SignalP 6.0 predicts all five types of signal peptides across bacteria, archaea, and eukarya."),),
        detection_methods=(M_SIGNALP6,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="sec_spi_translocation_and_cleavage",
                label="Sec-mediated secretory translocation and signal peptidase I proteolytic cleavage",
                mechanism_summary=(
                    "An N-terminal signal_peptide (SO:0000418) directs the nascent polypeptide into "
                    "protein transport by the Sec complex (GO:0043952), followed by signal peptidase I "
                    "endopeptidase activity (GO:0004175) at the Ala-X-Ala c-region motif to complete "
                    "protein secretion (GO:0009306)."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="SO:0000418",
                        label="signal_peptide",
                        node_type="MOTIF",
                        grounding="SO:0000418",
                        description="Tripartite N-terminal Sec/SPI secretory leader peptide (n-, h-, and AxA c-region).",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0043952",
                        label="protein transport by the Sec complex",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0043952",
                        description="Polypeptide translocation across the SecYEG/Sec61 translocon channel.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0004175",
                        label="endopeptidase activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0004175",
                        description="Type I signal peptidase (LepB/SPase I, EC:3.4.21.89) cleavage of the N-terminal leader.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0009306",
                        label="protein secretion",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0009306",
                        description="Release of the mature cleaved secretory protein across the membrane.",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="SO:0000418",
                        predicate="RO:0000057",
                        predicate_label="has participant",
                        object="GO:0043952",
                        description="The tripartite Sec/SPI signal peptide targets the preprotein to the SecYEG/Sec61 translocon.",
                        reference="PMID:34980915",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Signal peptides (SPs) are short N-terminal amino acid sequences that "
                            "target proteins to the secretory (Sec) or twin-arginine translocation "
                            "(Tat) pathways in prokaryotes and eukaryotes."
                        ),
                        notes="Sec targeting by N-terminal signal peptides (PMID:34980915).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0043952",
                        predicate="RO:0002411",
                        predicate_label="causally upstream of",
                        object="GO:0004175",
                        description="Translocation across the Sec channel exposes the c-region cleavage site to signal peptidase I.",
                        reference="PMID:34980915",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Sec/SPI SPs are transported by the Sec translocon and cleaved by "
                            "Signal Peptidase I (SPase I)."
                        ),
                        notes="Translocation precedes SPase I cleavage (PMID:34980915).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0004175",
                        predicate="RO:0002411",
                        predicate_label="causally upstream of",
                        object="GO:0009306",
                        description="Proteolytic removal of the signal peptide releases the mature secreted polypeptide.",
                        reference="PMID:34980915",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Sec/SPI SPs are transported by the Sec translocon and cleaved by "
                            "Signal Peptidase I (SPase I)."
                        ),
                        notes="SPase I cleavage releases mature secreted protein (PMID:34980915).",
                    ),
                ),
            ),
        ),
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
        parent_traits=("proteintraitsmech:UNIPROT_FT_SEQ_SIGNAL_PEPTIDE",),
        synonyms=(
            ("Sec/SPII signal peptide", "EXACT_SYNONYM"),
            ("bacterial lipoprotein lipobox signal peptide", "EXACT_SYNONYM"),
        ),
        sequence_pattern="[LVI][ASTVI][GAS]C",
        evidence=(("PMID:34980915", "Discrimination of Sec/SPII lipoprotein lipobox signal peptides by SignalP 6.0."),),
        detection_methods=(M_SIGNALP6,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="sec_spii_lipobox_diacylglyceryl_cleavage",
                label="Sec translocation, Lgt lipobox S-diacylglycerylation, and LspA signal peptidase II cleavage",
                mechanism_summary=(
                    "A lipobox signal_peptide (SO:0000418) mediates protein transport by the Sec "
                    "complex (GO:0043952), after which Lgt catalyzes protein lipidation (GO:0006497) "
                    "of the invariant +1 cysteine to S-diacylglycerol-L-cysteine (MOD:00138), "
                    "enabling LspA endopeptidase activity (GO:0004175) upstream of the lipidated cysteine."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="SO:0000418",
                        label="signal_peptide",
                        node_type="MOTIF",
                        grounding="SO:0000418",
                        description="Sec/SPII lipoprotein signal peptide carrying the C-terminal [LVI][ASTVI][GAS]C lipobox.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0043952",
                        label="protein transport by the Sec complex",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0043952",
                        description="SecYEG translocation of the prolipoprotein precursor.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0006497",
                        label="protein lipidation",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0006497",
                        description="Lgt-catalyzed S-diacylglyceryl transfer onto the lipobox +1 cysteine.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0004175",
                        label="endopeptidase activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0004175",
                        description="Lipoprotein signal peptidase II (LspA / SPase II, EC:3.4.23.36) cleavage upstream of +1 Cys.",
                    ),
                    CausalNodeSpec(
                        node_id="MOD:00138",
                        label="S-diacylglycerol-L-cysteine",
                        node_type="PTM",
                        grounding="MOD:00138",
                        description="Mature N-terminal S-diacylglyceryl-modified cysteine membrane anchor.",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="SO:0000418",
                        predicate="RO:0000057",
                        predicate_label="has participant",
                        object="GO:0043952",
                        description="The Sec/SPII leader directs the prolipoprotein across the Sec translocon.",
                        reference="PMID:34980915",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Sec/SPII SPs are lipoprotein signal peptides transported by the Sec "
                            "translocon and cleaved by Signal Peptidase II (SPase II, Lsp)."
                        ),
                        notes="Sec export of Sec/SPII prolipoproteins (PMID:34980915).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0043952",
                        predicate="RO:0002411",
                        predicate_label="causally upstream of",
                        object="GO:0006497",
                        description="Sec translocation presents the lipobox cysteine to prolipoprotein diacylglyceryl transferase (Lgt).",
                        reference="PMID:34980915",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Lipoprotein SPs contain a conserved C-terminal lipobox motif ending "
                            "with an invariant cysteine residue that is lipid-modified prior to "
                            "cleavage by SPase II."
                        ),
                        notes="Lipobox S-diacylglyceryl modification precedes SPase II cleavage (PMID:34980915).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0006497",
                        predicate="RO:0002411",
                        predicate_label="causally upstream of",
                        object="GO:0004175",
                        description="S-diacylglyceryl modification of the +1 cysteine is required for LspA (SPase II) cleavage.",
                        reference="PMID:34980915",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Lipoprotein SPs contain a conserved C-terminal lipobox motif ending "
                            "with an invariant cysteine residue that is lipid-modified prior to "
                            "cleavage by SPase II."
                        ),
                        notes="SPase II cleavage requires prior lipobox lipidation (PMID:34980915).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0004175",
                        predicate="RO:0002234",
                        predicate_label="has output",
                        object="MOD:00138",
                        description="SPase II cleavage exposes S-diacylglycerol-L-cysteine as the new N-terminal residue.",
                        reference="PMID:34980915",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Sec/SPII SPs are lipoprotein signal peptides transported by the Sec "
                            "translocon and cleaved by Signal Peptidase II (SPase II, Lsp)."
                        ),
                        notes="Mature N-terminal S-diacylglyceryl-cysteine lipoprotein (PMID:34980915).",
                    ),
                ),
            ),
        ),
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
        parent_traits=("proteintraitsmech:UNIPROT_FT_SEQ_SIGNAL_PEPTIDE",),
        synonyms=(
            ("Tat/SPI signal peptide", "EXACT_SYNONYM"),
            ("twin-arginine translocation signal peptide", "EXACT_SYNONYM"),
        ),
        sequence_pattern="[ST]RR[A-Z][FLV][LK]",
        evidence=(("PMID:34980915", "Prediction of Tat/SPI twin-arginine signal peptides with SignalP 6.0."),),
        detection_methods=(M_SIGNALP6,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="tat_spi_folded_export_and_cleavage",
                label="Twin-arginine (TatABC) folded protein translocation and signal peptidase I cleavage",
                mechanism_summary=(
                    "A twin-arginine signal_peptide (SO:0000418) is recognized by TatBC to drive "
                    "protein transport by the Tat complex (GO:0043953) of folded proteins, followed "
                    "by signal peptidase I endopeptidase activity (GO:0004175) to complete "
                    "protein secretion (GO:0009306)."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="SO:0000418",
                        label="signal_peptide",
                        node_type="MOTIF",
                        grounding="SO:0000418",
                        description="Tat/SPI leader peptide containing the [ST]RRxFLK twin-arginine motif.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0043953",
                        label="protein transport by the Tat complex",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0043953",
                        description="Export of folded proteins across the membrane by the TatABC translocase.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0004175",
                        label="endopeptidase activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0004175",
                        description="Signal peptidase I (LepB / SPase I) cleavage at the c-region AxA site.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0009306",
                        label="protein secretion",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0009306",
                        description="Release of the mature folded cofactor-containing protein.",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="SO:0000418",
                        predicate="RO:0000057",
                        predicate_label="has participant",
                        object="GO:0043953",
                        description="The twin-arginine motif targets folded preproteins to the Tat translocase.",
                        reference="PMID:34980915",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Tat SPs contain a canonical twin-arginine motif in the n-region and "
                            "direct folded proteins across the membrane via the Tat translocon."
                        ),
                        notes="Twin-arginine targeting to Tat translocon (PMID:34980915).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0043953",
                        predicate="RO:0002411",
                        predicate_label="causally upstream of",
                        object="GO:0004175",
                        description="Tat translocation exposes the c-region cleavage site to signal peptidase I.",
                        reference="PMID:34980915",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Tat/SPI SPs are transported by the Tat translocon and cleaved by "
                            "Signal Peptidase I (SPase I)."
                        ),
                        notes="Tat export followed by SPase I cleavage (PMID:34980915).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0004175",
                        predicate="RO:0002411",
                        predicate_label="causally upstream of",
                        object="GO:0009306",
                        description="SPase I cleavage releases the mature folded protein into the periplasm or extracellular space.",
                        reference="PMID:34980915",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Tat/SPI SPs are transported by the Tat translocon and cleaved by "
                            "Signal Peptidase I (SPase I)."
                        ),
                        notes="Release of mature Tat-exported protein (PMID:34980915).",
                    ),
                ),
            ),
        ),
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
        parent_traits=("proteintraitsmech:UNIPROT_FT_SEQ_SIGNAL_PEPTIDE",),
        synonyms=(
            ("Tat/SPII signal peptide", "EXACT_SYNONYM"),
            ("Tat lipoprotein signal peptide", "EXACT_SYNONYM"),
        ),
        evidence=(("PMID:34980915", "Identification of Tat/SPII twin-arginine lipoprotein signal peptides by SignalP 6.0."),),
        detection_methods=(M_SIGNALP6,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="tat_spii_folded_lipoprotein_processing",
                label="Tat translocation of folded prolipoprotein followed by lipobox lipidation and SPase II cleavage",
                mechanism_summary=(
                    "A Tat/SPII signal_peptide (SO:0000418) directs folded prolipoprotein export "
                    "via protein transport by the Tat complex (GO:0043953), followed by Lgt-mediated "
                    "protein lipidation (GO:0006497) and LspA endopeptidase activity (GO:0004175) "
                    "yielding an N-terminal S-diacylglycerol-L-cysteine (MOD:00138)."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="SO:0000418",
                        label="signal_peptide",
                        node_type="MOTIF",
                        grounding="SO:0000418",
                        description="Tat/SPII signal peptide combining an n-region RR motif with a c-region lipobox.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0043953",
                        label="protein transport by the Tat complex",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0043953",
                        description="Translocation of the folded prolipoprotein by TatABC.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0006497",
                        label="protein lipidation",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0006497",
                        description="S-diacylglyceryl modification of the lipobox +1 cysteine by Lgt.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0004175",
                        label="endopeptidase activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0004175",
                        description="Cleavage of the Tat/SPII leader peptide by lipoprotein signal peptidase II (LspA).",
                    ),
                    CausalNodeSpec(
                        node_id="MOD:00138",
                        label="S-diacylglycerol-L-cysteine",
                        node_type="PTM",
                        grounding="MOD:00138",
                        description="Mature N-terminal lipid-anchored cysteine residue.",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="SO:0000418",
                        predicate="RO:0000057",
                        predicate_label="has participant",
                        object="GO:0043953",
                        description="The Tat/SPII leader targets folded prolipoproteins to the Tat translocon.",
                        reference="PMID:34980915",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Tat/SPII SPs are transported by the Tat translocon and cleaved by "
                            "Signal Peptidase II (SPase II)."
                        ),
                        notes="Tat translocation of Tat/SPII prolipoproteins (PMID:34980915).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0043953",
                        predicate="RO:0002411",
                        predicate_label="causally upstream of",
                        object="GO:0006497",
                        description="Tat export delivers the c-region lipobox to Lgt for S-diacylglycerylation.",
                        reference="PMID:34980915",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Lipoprotein SPs contain a conserved C-terminal lipobox motif ending "
                            "with an invariant cysteine residue that is lipid-modified prior to "
                            "cleavage by SPase II."
                        ),
                        notes="Lipidation of Tat-exported prolipoprotein (PMID:34980915).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0006497",
                        predicate="RO:0002411",
                        predicate_label="causally upstream of",
                        object="GO:0004175",
                        description="Lipobox S-diacylglycerylation enables cleavage by SPase II (LspA).",
                        reference="PMID:34980915",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Tat/SPII SPs are transported by the Tat translocon and cleaved by "
                            "Signal Peptidase II (SPase II)."
                        ),
                        notes="SPase II cleavage of Tat/SPII leader (PMID:34980915).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0004175",
                        predicate="RO:0002234",
                        predicate_label="has output",
                        object="MOD:00138",
                        description="SPase II cleavage yields the mature N-terminal S-diacylglycerol-L-cysteine anchor.",
                        reference="PMID:34980915",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Lipoprotein SPs contain a conserved C-terminal lipobox motif ending "
                            "with an invariant cysteine residue that is lipid-modified prior to "
                            "cleavage by SPase II."
                        ),
                        notes="Mature lipid-anchored Tat/SPII lipoprotein (PMID:34980915).",
                    ),
                ),
            ),
        ),
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
        parent_traits=("proteintraitsmech:UNIPROT_FT_SEQ_SIGNAL_PEPTIDE",),
        synonyms=(
            ("Sec/SPIII signal peptide", "EXACT_SYNONYM"),
            ("type IV prepilin leader peptide", "EXACT_SYNONYM"),
        ),
        evidence=(("PMID:34980915", "Sec/SPIII prepilin signal peptide prediction in SignalP 6.0."),),
        detection_methods=(M_SIGNALP6,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="sec_spiii_prepilin_cleavage",
                label="Sec membrane insertion and prepilin peptidase (SPase III) cytoplasmic leader cleavage",
                mechanism_summary=(
                    "A short basic prepilin signal_peptide (SO:0000418) directs inner-membrane "
                    "insertion via protein transport by the Sec complex (GO:0043952), where "
                    "prepilin peptidase (PilD / SPase III) endopeptidase activity (GO:0004175) "
                    "cleaves after the conserved -1 glycine to drive pilin protein maturation (GO:0051604)."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="SO:0000418",
                        label="signal_peptide",
                        node_type="MOTIF",
                        grounding="SO:0000418",
                        description="Short basic N-terminal Sec/SPIII prepilin leader peptide.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0043952",
                        label="protein transport by the Sec complex",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0043952",
                        description="Sec-mediated insertion of the prepilin precursor into the cytoplasmic membrane.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0004175",
                        label="endopeptidase activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0004175",
                        description="Type IV prepilin peptidase (PilD / SPase III, EC:3.4.23.43) cleavage at the cytoplasmic face.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0051604",
                        label="protein maturation",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0051604",
                        description="Maturation and N-methylation of the type IV pilin subunit for filament assembly.",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="SO:0000418",
                        predicate="RO:0000057",
                        predicate_label="has participant",
                        object="GO:0043952",
                        description="The Sec/SPIII leader directs Sec-dependent membrane insertion of the prepilin.",
                        reference="PMID:34980915",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Sec/SPIII SPs are prepilin signal peptides transported by the Sec "
                            "translocon and cleaved by Signal Peptidase III (SPase III, prepilin peptidase)."
                        ),
                        notes="Sec insertion of Sec/SPIII prepilins (PMID:34980915).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0043952",
                        predicate="RO:0002411",
                        predicate_label="causally upstream of",
                        object="GO:0004175",
                        description="Membrane insertion positions the n/h boundary on the cytoplasmic side for SPase III cleavage.",
                        reference="PMID:34980915",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Unlike SPase I and II, SPase III cleaves the positively charged n-region "
                            "on the cytoplasmic side of the membrane just before the hydrophobic region."
                        ),
                        notes="Cytoplasmic-side cleavage by SPase III (PMID:34980915).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0004175",
                        predicate="RO:0002411",
                        predicate_label="causally upstream of",
                        object="GO:0051604",
                        description="SPase III leader excision and N-terminal methylation produce the mature pilin subunit.",
                        reference="PMID:34980915",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Sec/SPIII SPs are prepilin signal peptides transported by the Sec "
                            "translocon and cleaved by Signal Peptidase III (SPase III, prepilin peptidase)."
                        ),
                        notes="Prepilin maturation via SPase III (PMID:34980915).",
                    ),
                ),
            ),
        ),
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
        parent_traits=("proteintraitsmech:UNIPROT_FT_SEQ_TRANSIT_PEPTIDE",),
        synonyms=(
            ("mTP", "EXACT_SYNONYM"),
            ("mitochondrial presequence", "EXACT_SYNONYM"),
            ("mitochondrial matrix targeting signal", "EXACT_SYNONYM"),
        ),
        xrefs=("SO:0001073",),
        evidence=(("PMID:31609389", "TargetP 2.0 predicts mitochondrial, chloroplast, and thylakoid luminal transit peptides."),),
        detection_methods=(M_TARGETP2,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="mtp_tom_tim23_import_mpp_cleavage",
                label="TOM/TIM23 mitochondrial matrix import and MPP presequence cleavage",
                mechanism_summary=(
                    "An N-terminal mitochondrial_targeting_signal (SO:0001073) directs protein "
                    "import into mitochondrial matrix (GO:0030150) across the TOM and TIM23 "
                    "translocons, where the mitochondrial processing peptidase complex (GO:0017087) "
                    "cleaves the presequence to release the mature protein in the mitochondrial matrix (GO:0005759)."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="SO:0001073",
                        label="mitochondrial_targeting_signal",
                        node_type="MOTIF",
                        grounding="SO:0001073",
                        description="Amphipathic positively charged N-terminal mitochondrial presequence (mTP).",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0030150",
                        label="protein import into mitochondrial matrix",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0030150",
                        description="TOM/TIM23-mediated translocation of nuclear-encoded precursor proteins.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0017087",
                        label="mitochondrial processing peptidase complex",
                        node_type="PROTEIN",
                        grounding="GO:0017087",
                        description="Heterodimeric MPP metallopeptidase (EC:3.4.24.64) excising the N-terminal mTP.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0005759",
                        label="mitochondrial matrix",
                        node_type="CELLULAR_LOCALIZATION",
                        grounding="GO:0005759",
                        description="Destination mitochondrial matrix compartment of the cleaved mature protein.",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="SO:0001073",
                        predicate="RO:0000057",
                        predicate_label="has participant",
                        object="GO:0030150",
                        description="The amphipathic N-terminal presequence is recognized by TOM receptors to initiate matrix import.",
                        reference="PMID:31609389",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Mitochondrial transit peptides (mTPs) are N-terminal presequences that "
                            "direct nuclear-encoded proteins into the mitochondria and are cleaved "
                            "upon import by the mitochondrial processing peptidase (MPP)."
                        ),
                        notes="mTP targeting for mitochondrial matrix import (PMID:31609389).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0030150",
                        predicate="RO:0002411",
                        predicate_label="causally upstream of",
                        object="GO:0017087",
                        description="Translocation into the matrix exposes the presequence cleavage site to MPP.",
                        reference="PMID:31609389",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Mitochondrial transit peptides (mTPs) are N-terminal presequences that "
                            "direct nuclear-encoded proteins into the mitochondria and are cleaved "
                            "upon import by the mitochondrial processing peptidase (MPP)."
                        ),
                        notes="MPP cleavage of imported mitochondrial presequences (PMID:31609389).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0017087",
                        predicate="RO:0002411",
                        predicate_label="causally upstream of",
                        object="GO:0005759",
                        description="MPP proteolysis releases the mature folded protein within the mitochondrial matrix.",
                        reference="PMID:31609389",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Mitochondrial transit peptides (mTPs) are N-terminal presequences that "
                            "direct nuclear-encoded proteins into the mitochondria and are cleaved "
                            "upon import by the mitochondrial processing peptidase (MPP)."
                        ),
                        notes="Mature protein localization in the mitochondrial matrix (PMID:31609389).",
                    ),
                ),
            ),
        ),
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
        parent_traits=("proteintraitsmech:UNIPROT_FT_SEQ_TRANSIT_PEPTIDE",),
        synonyms=(
            ("cTP", "EXACT_SYNONYM"),
            ("chloroplast transit peptide", "EXACT_SYNONYM"),
            ("plastid targeting peptide", "BROAD_SYNONYM"),
        ),
        xrefs=("SO:0001074",),
        evidence=(("PMID:31609389", "TargetP 2.0 discriminates stromal chloroplast transit peptides (cTP) and cleavage sites."),),
        detection_methods=(M_TARGETP2,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="ctp_toc_tic_stromal_import_spp_cleavage",
                label="TOC/TIC chloroplast stromal import and stromal processing peptidase (SPP) cleavage",
                mechanism_summary=(
                    "A chloroplast_transit_peptide (SO:0001074) mediates protein import into "
                    "chloroplast stroma (GO:0045037) across the outer (TOC) and inner (TIC) "
                    "envelope translocons, where stromal processing peptidase endopeptidase "
                    "activity (GO:0004175) excises the cTP in the chloroplast stroma (GO:0009570)."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="SO:0001074",
                        label="chloroplast_transit_peptide",
                        node_type="MOTIF",
                        grounding="SO:0001074",
                        description="Ser/Thr-enriched N-terminal chloroplast stroma transit peptide (cTP).",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0045037",
                        label="protein import into chloroplast stroma",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0045037",
                        description="TOC/TIC-mediated translocation across the chloroplast envelope membranes.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0004175",
                        label="endopeptidase activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0004175",
                        description="Stromal processing peptidase (SPP, EC:3.4.24.65) cleavage of the cTP.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0009570",
                        label="chloroplast stroma",
                        node_type="CELLULAR_LOCALIZATION",
                        grounding="GO:0009570",
                        description="Chloroplast stromal compartment receiving the mature cleaved protein.",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="SO:0001074",
                        predicate="RO:0000057",
                        predicate_label="has participant",
                        object="GO:0045037",
                        description="The N-terminal cTP directs precursor translocation through the TOC/TIC machinery.",
                        reference="PMID:31609389",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Chloroplast transit peptides (cTPs) target proteins to the chloroplast "
                            "stroma via the TOC-TIC translocon complexes and are cleaved by the "
                            "stromal processing peptidase (SPP)."
                        ),
                        notes="cTP-mediated import into chloroplast stroma (PMID:31609389).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0045037",
                        predicate="RO:0002411",
                        predicate_label="causally upstream of",
                        object="GO:0004175",
                        description="Import into the stroma exposes the cTP cleavage site to stromal processing peptidase (SPP).",
                        reference="PMID:31609389",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Chloroplast transit peptides (cTPs) target proteins to the chloroplast "
                            "stroma via the TOC-TIC translocon complexes and are cleaved by the "
                            "stromal processing peptidase (SPP)."
                        ),
                        notes="SPP cleavage upon stromal import (PMID:31609389).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0004175",
                        predicate="RO:0002411",
                        predicate_label="causally upstream of",
                        object="GO:0009570",
                        description="SPP cleavage releases the mature protein in the chloroplast stroma.",
                        reference="PMID:31609389",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Chloroplast transit peptides (cTPs) target proteins to the chloroplast "
                            "stroma via the TOC-TIC translocon complexes and are cleaved by the "
                            "stromal processing peptidase (SPP)."
                        ),
                        notes="Mature stromal localization after SPP cleavage (PMID:31609389).",
                    ),
                ),
            ),
        ),
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
        parent_traits=("proteintraitsmech:UNIPROT_FT_SEQ_TRANSIT_PEPTIDE",),
        synonyms=(
            ("luTP", "EXACT_SYNONYM"),
            ("thylakoid luminal transit peptide", "EXACT_SYNONYM"),
        ),
        xrefs=("SO:0001075",),
        evidence=(("PMID:31609389", "TargetP 2.0 identifies bipartite thylakoid luminal transit peptides (luTP)."),),
        detection_methods=(M_TARGETP2,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="lutp_bipartite_stromal_thylakoid_import",
                label="Bipartite stromal TOC/TIC import, SPP intermediate cleavage, and thylakoid Sec/Tat + TPP processing",
                mechanism_summary=(
                    "A bipartite thylakoid_transit_peptide (SO:0001075) first directs protein "
                    "import into chloroplast stroma (GO:0045037) and SPP cleavage, exposing the "
                    "thylakoid transfer domain for protein import into chloroplast thylakoid "
                    "membrane (GO:0045038) and TPP endopeptidase activity (GO:0004175) to deliver "
                    "the mature protein into the chloroplast thylakoid lumen (GO:0009543)."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="SO:0001075",
                        label="thylakoid_transit_peptide",
                        node_type="MOTIF",
                        grounding="SO:0001075",
                        description="Bipartite plastid transit peptide (N-terminal cTP + C-terminal thylakoid transfer peptide).",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0045037",
                        label="protein import into chloroplast stroma",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0045037",
                        description="First-stage import across the chloroplast envelope via TOC/TIC and SPP cleavage.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0045038",
                        label="protein import into chloroplast thylakoid membrane",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0045038",
                        description="Second-stage translocation across the thylakoid membrane via cpSec1 or cpTat.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0004175",
                        label="endopeptidase activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0004175",
                        description="Thylakoidal processing peptidase (TPP / Plsp1, EC:3.4.21.89) cleavage at the AxA motif.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0009543",
                        label="chloroplast thylakoid lumen",
                        node_type="CELLULAR_LOCALIZATION",
                        grounding="GO:0009543",
                        description="Thylakoid lumen compartment where the mature protein resides.",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="SO:0001075",
                        predicate="RO:0000057",
                        predicate_label="has participant",
                        object="GO:0045037",
                        description="The N-terminal stromal targeting portion of the bipartite luTP directs TOC/TIC import.",
                        reference="PMID:31609389",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Proteins targeted to the thylakoid lumen carry a bipartite transit "
                            "peptide (luTP) composed of an N-terminal stromal targeting peptide "
                            "cleaved by SPP, followed by a thylakoid transfer peptide cleaved by "
                            "the thylakoidal processing peptidase (TPP)."
                        ),
                        notes="First-stage stromal import of bipartite luTP (PMID:31609389).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0045037",
                        predicate="RO:0002411",
                        predicate_label="causally upstream of",
                        object="GO:0045038",
                        description="Stromal import and SPP cleavage unmask the Sec/Tat thylakoid transfer peptide.",
                        reference="PMID:31609389",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Proteins targeted to the thylakoid lumen carry a bipartite transit "
                            "peptide (luTP) composed of an N-terminal stromal targeting peptide "
                            "cleaved by SPP, followed by a thylakoid transfer peptide cleaved by "
                            "the thylakoidal processing peptidase (TPP)."
                        ),
                        notes="Unmasking of thylakoid transfer peptide after stromal import (PMID:31609389).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0045038",
                        predicate="RO:0002411",
                        predicate_label="causally upstream of",
                        object="GO:0004175",
                        description="Thylakoid translocation presents the luminal AxA cleavage site to TPP.",
                        reference="PMID:31609389",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "The thylakoid transfer peptide directs translocation across the "
                            "thylakoid membrane via the cpSec or cpTat pathway and is cleaved "
                            "by TPP in the lumen."
                        ),
                        notes="Thylakoid translocation followed by TPP cleavage (PMID:31609389).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0004175",
                        predicate="RO:0002411",
                        predicate_label="causally upstream of",
                        object="GO:0009543",
                        description="TPP cleavage releases the mature protein into the chloroplast thylakoid lumen.",
                        reference="PMID:31609389",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "The thylakoid transfer peptide directs translocation across the "
                            "thylakoid membrane via the cpSec or cpTat pathway and is cleaved "
                            "by TPP in the lumen."
                        ),
                        notes="Release into chloroplast thylakoid lumen (PMID:31609389).",
                    ),
                ),
            ),
        ),
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
        parent_traits=("proteintraitsmech:UNIPROT_FT_SEQ_PROPEPTIDE",),
        synonyms=(
            ("zymogen activation peptide", "EXACT_SYNONYM"),
            ("autoinhibitory pro-domain", "EXACT_SYNONYM"),
        ),
        xrefs=("SO:0001062",),
        evidence=(("PMID:16002793", "Mechanisms of zymogen latency and proteolytic propeptide activation."),),
        detection_methods=(M_PROPEP,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="zymogen_propeptide_autoinhibition_and_activation",
                label="Autoinhibitory propeptide steric blockade and proteolytic zymogen activation",
                mechanism_summary=(
                    "An uncleaved propeptide (SO:0001062) exerts intramolecular enzyme inhibitor "
                    "activity (GO:0004857) that negatively regulates orthosteric catalytic activity "
                    "(GO:0003824); endopeptidase activity (GO:0004175) excises the propeptide to "
                    "drive zymogen activation (GO:0031638), positively regulating catalytic activity."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="SO:0001062",
                        label="propeptide",
                        node_type="MOTIF",
                        grounding="SO:0001062",
                        description="Cleavable autoinhibitory pro-domain or activation peptide of a zymogen.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0004857",
                        label="enzyme inhibitor activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0004857",
                        description="Steric active-site occlusion or cysteine-switch coordination maintaining zymogen latency.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0004175",
                        label="endopeptidase activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0004175",
                        description="Activating protease cleavage of the propeptide-catalytic domain junction.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0031638",
                        label="zymogen activation",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0031638",
                        description="Proteolytic removal of the inhibitory propeptide and active-site maturation.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0003824",
                        label="catalytic activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0003824",
                        description="Mature enzyme catalytic activity.",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="SO:0001062",
                        predicate="RO:0002327",
                        predicate_label="enables",
                        object="GO:0004857",
                        description="The intact propeptide sterically blocks the catalytic cleft to maintain latency.",
                        reference="PMID:16002793",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Many proteases are synthesized as inactive precursors, or zymogens, "
                            "with N-terminal propeptides that sterically block the active site to "
                            "prevent premature activation."
                        ),
                        notes="Steric active-site blockade by zymogen propeptides (PMID:16002793).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0004857",
                        predicate="RO:0002212",
                        predicate_label="negatively regulates",
                        object="GO:0003824",
                        description="Intramolecular propeptide inhibition suppresses catalytic activity in the zymogen.",
                        reference="PMID:16002793",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Many proteases are synthesized as inactive precursors, or zymogens, "
                            "with N-terminal propeptides that sterically block the active site to "
                            "prevent premature activation."
                        ),
                        notes="Negative regulation of catalysis in latent zymogen (PMID:16002793).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0004175",
                        predicate="RO:0002327",
                        predicate_label="enables",
                        object="GO:0031638",
                        description="Proteolytic cleavage of the propeptide triggers zymogen activation.",
                        reference="PMID:16002793",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Activation requires proteolytic cleavage and removal of the propeptide, "
                            "releasing the active mature enzyme."
                        ),
                        notes="Proteolytic cleavage drives zymogen activation (PMID:16002793).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0031638",
                        predicate="RO:0002213",
                        predicate_label="positively regulates",
                        object="GO:0003824",
                        description="Zymogen activation unmasks the catalytic site for full enzymatic activity.",
                        reference="PMID:16002793",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Activation requires proteolytic cleavage and removal of the propeptide, "
                            "releasing the active mature enzyme."
                        ),
                        notes="Unmasking of mature catalytic activity (PMID:16002793).",
                    ),
                ),
            ),
        ),
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
        parent_traits=("proteintraitsmech:UNIPROT_FT_SEQ_PROPEPTIDE",),
        synonyms=(
            ("IMC propeptide", "EXACT_SYNONYM"),
            ("folding-chaperone prodomain", "EXACT_SYNONYM"),
        ),
        xrefs=("SO:0001062",),
        evidence=(("PMID:16002793", "Intramolecular chaperone propeptides catalyze folding of their cognate protease domains."),),
        detection_methods=(M_PROPEP,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="imc_propeptide_folding_and_autocleavage",
                label="Intramolecular-chaperone propeptide catalyzes protease domain folding followed by autoprocessing",
                mechanism_summary=(
                    "An intramolecular-chaperone propeptide (SO:0001062) lowers the kinetic transition "
                    "barrier to positively regulate protein folding (GO:0006457) of the cognate protease "
                    "domain, which then acquires endopeptidase activity (GO:0004175) to cleave and "
                    "degrade the propeptide during zymogen activation (GO:0031638)."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="SO:0001062",
                        label="propeptide",
                        node_type="MOTIF",
                        grounding="SO:0001062",
                        description="Intramolecular chaperone (IMC) propeptide domain (e.g. subtilisin/alpha-lytic protease pro-region).",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0006457",
                        label="protein folding",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0006457",
                        description="Kinetically assisted folding of the mature protease domain.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0004175",
                        label="endopeptidase activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0004175",
                        description="Autocatalytic cleavage and proteolytic degradation of the IMC propeptide.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0031638",
                        label="zymogen activation",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0031638",
                        description="Release of the kinetically trapped, active mature protease after propeptide destruction.",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="SO:0001062",
                        predicate="RO:0002213",
                        predicate_label="positively regulates",
                        object="GO:0006457",
                        description="The IMC propeptide stabilizes the folding transition state of the catalytic domain.",
                        reference="PMID:16002793",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Propeptides of subtilisin and alpha-lytic protease act as intramolecular "
                            "chaperones that directly catalyze the folding of the catalytic domain "
                            "across a high kinetic barrier."
                        ),
                        notes="Intramolecular chaperone catalysis of protein folding (PMID:16002793).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0006457",
                        predicate="RO:0002411",
                        predicate_label="causally upstream of",
                        object="GO:0004175",
                        description="Folding of the protease domain forms the catalytic triad capable of autoprocessing.",
                        reference="PMID:16002793",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Once the protease domain folds into its native state, it autocatalytically "
                            "cleaves and degrades the propeptide to yield the active enzyme."
                        ),
                        notes="Folding enables autocatalytic endopeptidase activity (PMID:16002793).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0004175",
                        predicate="RO:0002411",
                        predicate_label="causally upstream of",
                        object="GO:0031638",
                        description="Autocatalytic cleavage and degradation of the IMC propeptide completes zymogen activation.",
                        reference="PMID:16002793",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Once the protease domain folds into its native state, it autocatalytically "
                            "cleaves and degrades the propeptide to yield the active enzyme."
                        ),
                        notes="Propeptide degradation completes enzyme activation (PMID:16002793).",
                    ),
                ),
            ),
        ),
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
        parent_traits=("proteintraitsmech:UNIPROT_FT_SEQ_PROPEPTIDE",),
        synonyms=(
            ("furin/prohormone convertase propeptide", "EXACT_SYNONYM"),
            ("proprotein convertase pro-region", "EXACT_SYNONYM"),
        ),
        xrefs=("SO:0001062",),
        sequence_pattern="[KR]R|[RK][A-Z]{2}R",
        evidence=(("PMID:22931919", "Biochemistry and substrate specificity of proprotein convertases and dibasic propeptides."),),
        detection_methods=(M_PROPEP,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="dibasic_propeptide_convertase_excision",
                label="Proprotein convertase cleavage at dibasic (KR/RR/RxxR) motifs excises propeptide for hormone maturation",
                mechanism_summary=(
                    "A dibasic-flanked propeptide (SO:0001062) is recognized by subtilisin/kexin-like "
                    "proprotein convertase endopeptidase activity (GO:0004175), driving proteolytic "
                    "protein processing (GO:0016485) and bioactive peptide/growth-factor protein "
                    "maturation (GO:0051604)."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="SO:0001062",
                        label="propeptide",
                        node_type="MOTIF",
                        grounding="SO:0001062",
                        description="Prohormone/growth-factor propeptide flanked by paired basic (KR, RR, RxxR) cleavage sites.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0004175",
                        label="endopeptidase activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0004175",
                        description="Proprotein convertase (PCSK1/PCSK2/furin, EC:3.4.21.93/EC:3.4.21.94/EC:3.4.21.75) cleavage C-terminal to basic pairs.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0016485",
                        label="protein processing",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0016485",
                        description="Endoproteolytic propeptide excision in the trans-Golgi network or secretory granules.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0051604",
                        label="protein maturation",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0051604",
                        description="Generation of the mature bioactive peptide hormone or growth factor.",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="SO:0001062",
                        predicate="RO:0000057",
                        predicate_label="has participant",
                        object="GO:0016485",
                        description="The dibasic-flanked propeptide serves as the recognition substrate for proprotein processing.",
                        reference="PMID:22931919",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "The proprotein convertases (PCs) are a family of nine secretory serine "
                            "proteases that cleave precursor proteins at single or paired basic "
                            "residues within the consensus motif (R/K)-(X)n-(R/K)."
                        ),
                        notes="Dibasic propeptide recognition by proprotein convertases (PMID:22931919).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0004175",
                        predicate="RO:0002327",
                        predicate_label="enables",
                        object="GO:0016485",
                        description="Proprotein convertase endopeptidase activity cleaves C-terminal to the KR/RR/RxxR site.",
                        reference="PMID:22931919",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "The proprotein convertases (PCs) are a family of nine secretory serine "
                            "proteases that cleave precursor proteins at single or paired basic "
                            "residues within the consensus motif (R/K)-(X)n-(R/K)."
                        ),
                        notes="Endoproteolytic cleavage at dibasic motifs (PMID:22931919).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0016485",
                        predicate="RO:0002411",
                        predicate_label="causally upstream of",
                        object="GO:0051604",
                        description="Excision of the propeptide produces the mature bioactive hormone or growth factor.",
                        reference="PMID:22931919",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Cleavage of the propeptide by PCs in the trans-Golgi network or "
                            "secretory granules is required for the maturation of polypeptide "
                            "hormones, neuropeptides, and growth factors."
                        ),
                        notes="Propeptide excision yields mature bioactive peptide (PMID:22931919).",
                    ),
                ),
            ),
        ),
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
        causal_graphs=(
            CausalGraphSpec(
                graph_id="intrachain_disulfide_oxidative_folding",
                label="Oxidative thiol-disulfide crosslinking of intrachain cysteines stabilizes tertiary protein folding",
                mechanism_summary=(
                    "Protein disulfide isomerase activity (GO:0003756) oxidizes paired L-cysteine "
                    "residues (CHEBI:29950) within the same polypeptide chain to form an intrachain "
                    "L-cystine (cross-link) (MOD:00034), reducing unfolded chain entropy to positively "
                    "regulate tertiary protein folding (GO:0006457)."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="CHEBI:29950",
                        label="L-cysteine residue",
                        node_type="RESIDUE",
                        grounding="CHEBI:29950",
                        description="Paired reduced L-cysteine thiolates within the same polypeptide chain.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0003756",
                        label="protein disulfide isomerase activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0003756",
                        description="Thiol-disulfide oxidoreductase/isomerase (PDI / DsbA, EC:5.3.4.1) catalyzing cystine formation.",
                    ),
                    CausalNodeSpec(
                        node_id="MOD:00034",
                        label="L-cystine (cross-link)",
                        node_type="PTM",
                        grounding="MOD:00034",
                        description="Intrachain covalent cystine disulfide bridge.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0006457",
                        label="protein folding",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0006457",
                        description="Thermodynamic stabilization of native tertiary structure via unfolded-state entropy reduction.",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="GO:0003756",
                        predicate="RO:0002233",
                        predicate_label="has input",
                        object="CHEBI:29950",
                        description="Protein disulfide oxidoreductase/isomerase oxidizes two intrachain L-cysteine thiolates.",
                        reference="PMID:17001100",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Disulfide bonds form by the oxidation of pairs of cysteine residues and "
                            "stabilize the native tertiary structure of proteins by decreasing the "
                            "conformational entropy of the unfolded state."
                        ),
                        notes="Oxidation of paired intrachain cysteine residues (PMID:17001100).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0003756",
                        predicate="RO:0002234",
                        predicate_label="has output",
                        object="MOD:00034",
                        description="Oxidative thiol coupling yields a covalent intrachain L-cystine crosslink.",
                        reference="PMID:17001100",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Disulfide bonds form by the oxidation of pairs of cysteine residues and "
                            "stabilize the native tertiary structure of proteins by decreasing the "
                            "conformational entropy of the unfolded state."
                        ),
                        notes="Formation of intrachain cystine crosslink (PMID:17001100).",
                    ),
                    CausalEdgeSpec(
                        subject="MOD:00034",
                        predicate="RO:0002213",
                        predicate_label="positively regulates",
                        object="GO:0006457",
                        description="The intrachain cystine crosslink restricts unfolded-state entropy and stabilizes native folding.",
                        reference="PMID:17001100",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Disulfide bonds form by the oxidation of pairs of cysteine residues and "
                            "stabilize the native tertiary structure of proteins by decreasing the "
                            "conformational entropy of the unfolded state."
                        ),
                        notes="Entropic stabilization of tertiary fold (PMID:17001100).",
                    ),
                ),
            ),
        ),
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
        causal_graphs=(
            CausalGraphSpec(
                graph_id="interchain_disulfide_quaternary_crosslinking",
                label="Inter-subunit cystine crosslinking covalently stabilizes quaternary dimer/oligomer assembly",
                mechanism_summary=(
                    "Protein disulfide isomerase activity (GO:0003756) oxidizes L-cysteine residues "
                    "(CHEBI:29950) across juxtaposed polypeptide subunits to form an interchain "
                    "L-cystine (cross-link) (MOD:00034) that covalently stabilizes protein "
                    "heterodimerization activity (GO:0046982) and homodimerization."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="CHEBI:29950",
                        label="L-cysteine residue",
                        node_type="RESIDUE",
                        grounding="CHEBI:29950",
                        description="Cysteine residues positioned across an inter-subunit quaternary interface.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0003756",
                        label="protein disulfide isomerase activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0003756",
                        description="Oxidative thiol-disulfide formation across partner polypeptide chains.",
                    ),
                    CausalNodeSpec(
                        node_id="MOD:00034",
                        label="L-cystine (cross-link)",
                        node_type="PTM",
                        grounding="MOD:00034",
                        description="Interchain covalent cystine disulfide bridge linking two subunits.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0046982",
                        label="protein heterodimerization activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0046982",
                        description="Covalent quaternary subunit assembly (e.g., immunoglobulin H-L or insulin A-B chains).",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="GO:0003756",
                        predicate="RO:0002233",
                        predicate_label="has input",
                        object="CHEBI:29950",
                        description="Oxidative disulfide formation consumes juxtaposed cysteine thiols on partner chains.",
                        reference="PMID:17001100",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Interchain disulfide bonds covalently link distinct polypeptide chains "
                            "and stabilize quaternary structure in secreted and cell-surface oligomers."
                        ),
                        notes="Inter-subunit cysteine oxidation (PMID:17001100).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0003756",
                        predicate="RO:0002234",
                        predicate_label="has output",
                        object="MOD:00034",
                        description="Oxidation forms an inter-polypeptide L-cystine covalent bridge.",
                        reference="PMID:17001100",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Interchain disulfide bonds covalently link distinct polypeptide chains "
                            "and stabilize quaternary structure in secreted and cell-surface oligomers."
                        ),
                        notes="Interchain cystine crosslink formation (PMID:17001100).",
                    ),
                    CausalEdgeSpec(
                        subject="MOD:00034",
                        predicate="RO:0002213",
                        predicate_label="positively regulates",
                        object="GO:0046982",
                        description="The interchain cystine crosslink locks subunit stoichiometry against dissociation.",
                        reference="PMID:17001100",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Interchain disulfide bonds covalently link distinct polypeptide chains "
                            "and stabilize quaternary structure in secreted and cell-surface oligomers."
                        ),
                        notes="Covalent stabilization of quaternary dimer/oligomer assembly (PMID:17001100).",
                    ),
                ),
            ),
        ),
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
        causal_graphs=(
            CausalGraphSpec(
                graph_id="cystine_knot_threaded_macrocycle_stability",
                label="Threaded three-disulfide cystine-knot topology locks tertiary fold and resists proteolysis",
                mechanism_summary=(
                    "Six conserved L-cysteine residues (CHEBI:29950) oxidize into three interlocked "
                    "L-cystine (cross-link) bridges (MOD:00034) where CysIII-CysVI threads the "
                    "CysI-CysIV / CysII-CysV ring, locking native protein folding (GO:0006457) and "
                    "negatively regulating proteolytic cleavage by endopeptidase activity (GO:0004175)."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="CHEBI:29950",
                        label="L-cysteine residue",
                        node_type="RESIDUE",
                        grounding="CHEBI:29950",
                        description="Six conserved cysteine residues (CysI-CysVI) arranged in a knottin sequence pattern.",
                    ),
                    CausalNodeSpec(
                        node_id="MOD:00034",
                        label="L-cystine (cross-link)",
                        node_type="PTM",
                        grounding="MOD:00034",
                        description="Threaded three-disulfide (CysI-CysIV, CysII-CysV, CysIII-CysVI) cystine-knot network.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0006457",
                        label="protein folding",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0006457",
                        description="Hyperstable knotted tertiary fold resistant to thermal and chemical denaturation.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0004175",
                        label="endopeptidase activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0004175",
                        description="Host or digestive endopeptidase attack resisted by the rigid cystine-knot core.",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="CHEBI:29950",
                        predicate="RO:0002411",
                        predicate_label="causally upstream of",
                        object="MOD:00034",
                        description="Six conserved cysteines pair in the I-IV, II-V, III-VI threaded cystine-knot connectivity.",
                        reference="PMID:19569188",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "The cystine knot comprises an embedded ring formed by two disulfide "
                            "bonds (CysI-CysIV and CysII-CysV) and their connecting backbone "
                            "segments, which is threaded by a third disulfide bond (CysIII-CysVI)."
                        ),
                        notes="Threaded three-disulfide connectivity of cystine knots (PMID:19569188).",
                    ),
                    CausalEdgeSpec(
                        subject="MOD:00034",
                        predicate="RO:0002213",
                        predicate_label="positively regulates",
                        object="GO:0006457",
                        description="The threaded cystine-knot topology locks the compact tertiary fold against unfolding.",
                        reference="PMID:19569188",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "This knotted arrangement of three disulfide bonds confers exceptional "
                            "thermal, chemical, and proteolytic stability to cystine-knot proteins."
                        ),
                        notes="Hyperstability of cystine-knot fold (PMID:19569188).",
                    ),
                    CausalEdgeSpec(
                        subject="MOD:00034",
                        predicate="RO:0002212",
                        predicate_label="negatively regulates",
                        object="GO:0004175",
                        description="Compact threaded crosslinking prevents backbone unfolding required for endopeptidase cleavage.",
                        reference="PMID:19569188",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "This knotted arrangement of three disulfide bonds confers exceptional "
                            "thermal, chemical, and proteolytic stability to cystine-knot proteins."
                        ),
                        notes="Resistance to proteolytic degradation (PMID:19569188).",
                    ),
                ),
            ),
        ),
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
        causal_graphs=(
            CausalGraphSpec(
                graph_id="allosteric_disulfide_redox_switch_regulation",
                label="Reversible thiol-disulfide exchange of high-strain cystine bond switches protein activity",
                mechanism_summary=(
                    "Protein-disulfide reductase activity (GO:0015035) reversibly cleaves a high-strain "
                    "-RHStaple/-LHHook L-cystine (cross-link) (MOD:00034) into reduced L-cysteine "
                    "residues (CHEBI:29950), driving conformational enzyme regulator activity "
                    "(GO:0030234) and cell redox homeostasis (GO:0045454)."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="MOD:00034",
                        label="L-cystine (cross-link)",
                        node_type="PTM",
                        grounding="MOD:00034",
                        description="High-strain allosteric or catalytic disulfide bond (-RHStaple / +/-RHHook / -LHHook).",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0015035",
                        label="protein-disulfide reductase activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0015035",
                        description="Thioredoxin/glutaredoxin oxidoreductase cleaving the strained disulfide bond.",
                    ),
                    CausalNodeSpec(
                        node_id="CHEBI:29950",
                        label="L-cysteine residue",
                        node_type="RESIDUE",
                        grounding="CHEBI:29950",
                        description="Reduced dithiol cysteine pair generated upon disulfide cleavage.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0030234",
                        label="enzyme regulator activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0030234",
                        description="Redox-coupled conformational switch regulating target protein function.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0045454",
                        label="cell redox homeostasis",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0045454",
                        description="Dithiol-disulfide redox signaling and homeostasis.",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="GO:0015035",
                        predicate="RO:0002233",
                        predicate_label="has input",
                        object="MOD:00034",
                        description="Oxidoreductases reduce the high-strain allosteric cystine disulfide bond.",
                        reference="PMID:17001100",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Allosteric disulfides control the function of the mature protein in "
                            "which they reside when they are cleaved or formed by oxidoreductases, "
                            "and typically adopt a high-strain -RHStaple configuration."
                        ),
                        notes="Reduction of strained -RHStaple allosteric disulfides (PMID:17001100).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0015035",
                        predicate="RO:0002234",
                        predicate_label="has output",
                        object="CHEBI:29950",
                        description="Reductive cleavage converts the cystine crosslink into a pair of L-cysteine thiols.",
                        reference="PMID:24743683",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Cleavage of allosteric disulfide bonds by thiol-disulfide exchange or "
                            "oxidoreductases induces a conformational change that switches protein "
                            "ligand binding or enzymatic activity."
                        ),
                        notes="Dithiol formation upon disulfide cleavage (PMID:24743683).",
                    ),
                    CausalEdgeSpec(
                        subject="CHEBI:29950",
                        predicate="RO:0002411",
                        predicate_label="causally upstream of",
                        object="GO:0030234",
                        description="Release of dihedral disulfide strain triggers a conformational switch in protein activity.",
                        reference="PMID:24743683",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Cleavage of allosteric disulfide bonds by thiol-disulfide exchange or "
                            "oxidoreductases induces a conformational change that switches protein "
                            "ligand binding or enzymatic activity."
                        ),
                        notes="Conformational switch upon disulfide reduction (PMID:24743683).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0015035",
                        predicate="RO:0002331",
                        predicate_label="involved in",
                        object="GO:0045454",
                        description="Reversible dithiol-disulfide exchange mediates cellular redox regulation.",
                        reference="PMID:17001100",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Catalytic and allosteric disulfides mediate thiol-disulfide exchange "
                            "reactions essential for cellular redox homeostasis and signaling."
                        ),
                        notes="Role in cellular redox homeostasis (PMID:17001100).",
                    ),
                ),
            ),
        ),
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
        xrefs=("EC:1.13.11.3", "GO:0018578", "RHEA:10084"),
        evidence=(("PMID:2563464", "Crystal structure of protocatechuate 3,4-dioxygenase from Pseudomonas aeruginosa."),),
        detection_methods=(M_GO_COMPLEX,),
        definition_source="GO / CellStructureMech cross-Mech alignment",
        causal_graphs=(
            CausalGraphSpec(
                graph_id="pcagh_intradiol_ortho_cleavage",
                label="Non-heme Fe(III)-dependent intradiol ortho-cleavage of protocatechuate by the PcaGH complex",
                mechanism_summary=(
                    "The heterooligomeric protocatechuate 3,4-dioxygenase complex (GO:7770085) "
                    "coordinates a catalytic iron(3+) cofactor (CHEBI:29034) at the PcaH beta-subunit "
                    "active site to enable protocatechuate 3,4-dioxygenase activity (GO:0018578 / "
                    "EC:1.13.11.3 / RHEA:10084), converting 3,4-dihydroxybenzoate (CHEBI:36062) and "
                    "dioxygen (CHEBI:15379) into 3-carboxy-cis,cis-muconate (CHEBI:17440) in "
                    "protocatechuate catabolic process, ortho-cleavage (GO:0019618)."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="GO:7770085",
                        label="protocatechuate 3,4-dioxygenase complex",
                        node_type="PROTEIN",
                        grounding="GO:7770085",
                        description="Alpha-beta (PcaGH)n heterooligomeric non-heme ferric dioxygenase complex.",
                    ),
                    CausalNodeSpec(
                        node_id="CHEBI:29034",
                        label="iron(3+)",
                        node_type="CHEMICAL",
                        grounding="CHEBI:29034",
                        description="Catalytic non-heme high-spin Fe(III) ion coordinated by 2 Tyr, 2 His, and OH- in PcaH.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0018578",
                        label="protocatechuate 3,4-dioxygenase activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0018578",
                        description="Intradiol ring-cleaving dioxygenase catalysis (EC:1.13.11.3 / RHEA:10084).",
                    ),
                    CausalNodeSpec(
                        node_id="CHEBI:36062",
                        label="3,4-dihydroxybenzoate",
                        node_type="CHEMICAL",
                        grounding="CHEBI:36062",
                        description="Protocatechuate aromatic substrate chelating the active-site Fe(III).",
                    ),
                    CausalNodeSpec(
                        node_id="CHEBI:17440",
                        label="3-carboxy-cis,cis-muconate",
                        node_type="CHEMICAL",
                        grounding="CHEBI:17440",
                        description="Ring-opened intradiol ortho-cleavage product entering the beta-ketoadipate pathway.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0019618",
                        label="protocatechuate catabolic process, ortho-cleavage",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0019618",
                        description="Aerobic protocatechuate ortho-cleavage branch of the beta-ketoadipate pathway.",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="GO:7770085",
                        predicate="RO:0000057",
                        predicate_label="has participant",
                        object="CHEBI:29034",
                        description="The PcaGH complex coordinates a mononuclear non-heme Fe(III) center at the alpha-beta interface.",
                        reference="PMID:2563464",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "The active site is located at the interface between the alpha and beta "
                            "subunits, with the catalytic ferric ion ligated by two tyrosines and "
                            "two histidines from the beta subunit."
                        ),
                        notes="Active-site Fe(III) coordination in 3,4-PCD crystal structure (PMID:2563464).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:7770085",
                        predicate="RO:0002327",
                        predicate_label="enables",
                        object="GO:0018578",
                        description="The PcaGH alpha-beta holoenzyme enables protocatechuate 3,4-dioxygenase catalysis.",
                        reference="PMID:2563464",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "Protocatechuate 3,4-dioxygenase (3,4-PCD) is a non-heme iron-containing "
                            "bacterial enzyme that catalyzes the intradiol cleavage of "
                            "3,4-dihydroxybenzoate to beta-carboxy-cis,cis-muconate."
                        ),
                        notes="3,4-PCD holoenzyme catalytic activity (PMID:2563464).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0018578",
                        predicate="RO:0002233",
                        predicate_label="has input",
                        object="CHEBI:36062",
                        description="Protocatechuate 3,4-dioxygenase binds 3,4-dihydroxybenzoate as aromatic substrate.",
                        reference="PMID:2563464",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "Protocatechuate 3,4-dioxygenase (3,4-PCD) is a non-heme iron-containing "
                            "bacterial enzyme that catalyzes the intradiol cleavage of "
                            "3,4-dihydroxybenzoate to beta-carboxy-cis,cis-muconate."
                        ),
                        notes="Protocatechuate substrate binding (PMID:2563464).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0018578",
                        predicate="RO:0002234",
                        predicate_label="has output",
                        object="CHEBI:17440",
                        description="Intradiol dioxygenation cleaves the C3-C4 bond to yield 3-carboxy-cis,cis-muconate.",
                        reference="PMID:2563464",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "Protocatechuate 3,4-dioxygenase (3,4-PCD) is a non-heme iron-containing "
                            "bacterial enzyme that catalyzes the intradiol cleavage of "
                            "3,4-dihydroxybenzoate to beta-carboxy-cis,cis-muconate."
                        ),
                        notes="Formation of 3-carboxy-cis,cis-muconate (PMID:2563464).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0018578",
                        predicate="RO:0002331",
                        predicate_label="involved in",
                        object="GO:0019618",
                        description="Protocatechuate 3,4-dioxygenase catalyzes the committed ring-cleavage step of ortho-pathway catabolism.",
                        reference="PMID:2563464",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "Protocatechuate 3,4-dioxygenase (3,4-PCD) is a non-heme iron-containing "
                            "bacterial enzyme that catalyzes the intradiol cleavage of "
                            "3,4-dihydroxybenzoate to beta-carboxy-cis,cis-muconate."
                        ),
                        notes="Committed step of protocatechuate ortho-cleavage pathway (PMID:2563464).",
                    ),
                ),
            ),
        ),
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
    if spec.causal_graphs:
        lines.append("causal_graphs:")
        for cg in spec.causal_graphs:
            lines.append(f"  - graph_id: {cg.graph_id}")
            lines.append(f"    title: {yaml_escape(cg.label)}")
            lines.append(f"    description: {yaml_escape(cg.mechanism_summary)}")
            lines.append("    nodes:")
            for n in cg.nodes:
                lines.append(f"      - node_id: {yaml_escape(n.node_id)}")
                lines.append(f"        label: {yaml_escape(n.label)}")
                lines.append(f"        node_type: {n.node_type}")
                lines.append(f"        grounding: {yaml_escape(n.grounding)}")
                lines.append(f"        description: {yaml_escape(n.description)}")
            lines.append("    edges:")
            for e in cg.edges:
                lines.append(f"      - subject: {yaml_escape(e.subject)}")
                lines.append(f"        predicate: {yaml_escape(e.predicate_label)}")
                lines.append(f"        predicate_id: {e.predicate}")
                lines.append(f"        object: {yaml_escape(e.object)}")
                lines.append(f"        description: {yaml_escape(e.description)}")
                lines.append("        evidence:")
                lines.append(f"          - reference: {e.reference}")
                lines.append(f"            snippet: {yaml_escape(e.snippet)}")
                lines.append(f"            notes: {yaml_escape(f'{e.notes} ({e.evidence_code})')}")
    if spec.evidence:
        lines.append("evidence:")
        for ref, notes in spec.evidence:
            lines.append(f"  - reference: {ref}")
            lines.append(f"    notes: {yaml_escape(notes)}")
    if spec.causal_graphs:
        lines.append("curation_history:")
        lines.append("  - timestamp: '2026-10-21T03:30:00Z'")
        lines.append("    curator: claude")
        lines.append("    action: EDIT")
        lines.append(
            "    changes: Added literature-grounded causal_graphs mechanism "
            "representation and verified parent_traits hierarchy."
        )
        lines.append("    llm_assisted: true")
    lines.append(f"license: {LICENSE}")
    return "\n".join(lines) + "\n"


def go_0016937_seed() -> tuple[Path, str | None]:
    """Return path and updated payload to merge obsolete GO:0004085 into GO:0016937."""
    path = (
        TRAITS_DIR
        / "function"
        / "molecular_function"
        / "go"
        / "short-chain-fatty-acyl-coa-dehydrogenase-activity-go0016937.yaml"
    )
    if not path.exists():
        return path, None
    existing = path.read_text(encoding="utf-8")
    if "GO:0004085" in existing:
        return path, existing
    return path, append_to_section(existing, "xrefs", "xrefs:\n- GO:0004085\n")


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
            write_record(path, emit_record(spec), merge=not args.force, validate=True)
            written += 1

    # Also merge GO:0004085 alt_id into existing GO:0016937 record if not already present.
    go_path, go_seed = go_0016937_seed()
    go_updated = False
    if go_seed is not None:
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
