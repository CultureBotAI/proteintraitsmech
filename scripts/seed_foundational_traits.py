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

Expands the single-record and sparse categories where canonical subclasses were absent:
  - SEQ_SIGNAL_PEPTIDE       (data/traits/sequence/signal_peptide/)
  - SEQ_TRANSIT_PEPTIDE      (data/traits/sequence/transit_peptide/)
  - SEQ_PROPEPTIDE           (data/traits/sequence/propeptide/)
  - SEQ_INITIATOR_METHIONINE (data/traits/sequence/initiator_methionine/)
  - SEQ_MATURE_CHAIN         (data/traits/sequence/mature_chain/)
  - STRUCT_DISULFIDE         (data/traits/structure/disulfide/)
  - STRUCT_CAVITY            (data/traits/structure/cavity/)
  - STRUCT_SURFACE           (data/traits/structure/surface/)
  - STRUCT_DYNAMICS          (data/traits/structure/dynamics/)
  - EVO_CONSERVATION         (data/traits/evolution/conservation/)

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
    evolutionary_scope: tuple[tuple[str, object], ...] = ()
    definition_source: str = DEF_SOURCE


M_SECIS = MethodSpec(
    name="SecMarker / Infernal SECIS + TGA selenoprotein prediction",
    method_type="HMM_PROFILE",
    edam_operation="EDAM:operation_0415",
    tool="https://secmarker.crg.es/",
    evidence_code="ECO:0000255",
    reference="PMID:28192430",
    recipe="cmsearch --cpu 4 --tblout {output} RF00031.cm {input}",
)
M_PYL = MethodSpec(
    name="HMMER PylRS/tRNA(Pyl) & in-frame UAG pyrrolysine detection",
    method_type="HMM_PROFILE",
    edam_operation="EDAM:operation_0300",
    tool="biotools:hmmer3",
    evidence_code="ECO:0000259",
    reference="PMID:42848426",
    recipe="hmmsearch --cut_ga --domtblout {output} PylB_PylC_PylD.hmm {input}",
)
M_FMET = MethodSpec(
    name="N-terminal initiator fMet / deformylase motif scan",
    method_type="SEQUENCE_PATTERN",
    edam_operation="EDAM:operation_0239",
    tool="biotools:emboss",
    evidence_code="ECO:0000255",
    reference="PMID:42079159",
    recipe="fuzzpro -sequence {input} -pattern '^M[ACDEFGHIKLMNPQRSTVWY]' -outfile {output}",
)
M_DAMINO = MethodSpec(
    name="Radical-SAM epimerase / post-translational D-residue HMM scan",
    method_type="HMM_PROFILE",
    edam_operation="EDAM:operation_0300",
    tool="biotools:hmmer3",
    evidence_code="ECO:0000259",
    reference="PMID:29779654",
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
    reference="PMID:41809595",
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
M_MAP_NME_EXCISED = MethodSpec(
    name="TermiNator / EMBOSS fuzzpro penultimate-residue N-terminal methionine excision scan",
    method_type="SEQUENCE_PATTERN",
    edam_operation="EDAM:operation_0422",
    tool="biotools:emboss",
    evidence_code="ECO:0000255",
    reference="PMID:2682640",
    recipe="fuzzpro -sequence {input} -pattern '^M[GASPTVC]' -outfile {output}",
)
M_MAP_NME_RETAINED = MethodSpec(
    name="TermiNator / EMBOSS fuzzpro bulky penultimate-residue N-terminal methionine retention scan",
    method_type="SEQUENCE_PATTERN",
    edam_operation="EDAM:operation_0422",
    tool="biotools:emboss",
    evidence_code="ECO:0000255",
    reference="PMID:2682640",
    recipe="fuzzpro -sequence {input} -pattern '^M[RNDQEHLKMFPWYI]' -outfile {output}",
)
M_FMET_PDF = MethodSpec(
    name="N-terminal initiator fMet / peptide deformylase substrate scan",
    method_type="SEQUENCE_PATTERN",
    edam_operation="EDAM:operation_0239",
    tool="biotools:emboss",
    evidence_code="ECO:0000255",
    reference="PMID:18718933",
    recipe="fuzzpro -sequence {input} -pattern '^M[ACDEFGHIKLMNPQRSTVWY]' -outfile {output}",
)
M_NAT_PRED = MethodSpec(
    name="NetAcet / N-terminal acetyltransferase (NatB/NatC/NatE) substrate motif scan",
    method_type="SEQUENCE_PATTERN",
    edam_operation="EDAM:operation_0417",
    tool="biotools:netacet",
    evidence_code="ECO:0000255",
    reference="PMID:27498224",
    recipe="fuzzpro -sequence {input} -pattern '^M[DENQFLIWYKM]' -outfile {output}",
)
M_TARGETP2_V2 = MethodSpec(
    name="TargetP 2.0 mitochondrial / chloroplast / thylakoid transit peptide predictor",
    method_type="ML_PREDICTOR",
    edam_operation="EDAM:operation_2489",
    tool="biotools:targetp",
    evidence_code="ECO:0000255",
    reference="PMID:31601689",
    recipe="targetp -fasta {input} -org pl -format short -prefix {output}",
)
M_INTEIN = MethodSpec(
    name="InterProScan / Pfam Hint-domain & intein splice-junction HMM scan",
    method_type="HMM_PROFILE",
    edam_operation="EDAM:operation_0300",
    tool="biotools:interproscan",
    evidence_code="ECO:0000259",
    reference="PMID:24695729",
    recipe="interproscan.sh -i {input} -appl Pfam,ProSiteProfiles -f tsv -o {output}",
)
M_CAVER = MethodSpec(
    name="CAVER 3.0 / MOLE 2.5 Voronoi tunnel, pore & channel geometry calculation",
    method_type="STRUCTURAL_ALGORITHM",
    edam_operation="EDAM:operation_0250",
    tool="biotools:caver",
    evidence_code="ECO:0007669",
    reference="PMID:23093919",
    recipe="java -Xmx4g -jar caver.jar -home . -pdb {input} -conf config.txt -out {output}",
)
M_BUSCO = MethodSpec(
    name="BUSCO / OrthoDB universal single-copy ortholog HMM profile search",
    method_type="HMM_PROFILE",
    edam_operation="EDAM:operation_3745",
    tool="biotools:busco",
    evidence_code="ECO:0000265",
    reference="PMID:26059717",
    recipe="busco -i {input} -m proteins -l auto-lineage -o {output}",
)
M_CODEML_HYPHY = MethodSpec(
    name="PAML codeml / HyPhy codon maximum-likelihood dN/dS (omega) selection test",
    method_type="HOMOLOGY_TRANSFER",
    edam_operation="EDAM:operation_0554",
    tool="biotools:paml",
    evidence_code="ECO:0007669",
    reference="PMID:17483113",
    recipe="codeml codeml.ctl",
)
M_FREESASA = MethodSpec(
    name="FreeSASA / APBS solvent-accessible surface area & electrostatic patch calculation",
    method_type="STRUCTURAL_ALGORITHM",
    edam_operation="EDAM:operation_0387",
    tool="biotools:freesasa",
    evidence_code="ECO:0007669",
    reference="PMID:26973785",
    recipe="freesasa --format=json {input} > {output}",
)
M_PRODY_ANM = MethodSpec(
    name="ProDy / ANM anisotropic network model & conformational ensemble PCA",
    method_type="STRUCTURAL_ALGORITHM",
    edam_operation="EDAM:operation_0244",
    tool="biotools:prody",
    evidence_code="ECO:0007669",
    reference="PMID:21471012",
    recipe="prody anm {input} -n 20 -o {output}",
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
        xrefs=("SO:0001455", "MOD:00031", "CHEBI:30000"),
        evidence=(("PMID:28192430", "Secmarker identifies tRNASec and UGA recoding across selenoprotein-encoding genomes."),),
        detection_methods=(M_SECIS,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="secis_selenocysteine_incorporation",
                label="SECIS-directed cotranslational selenocysteine incorporation at UGA",
                mechanism_summary=(
                    "A cis-acting SECIS stem-loop RNA element (SO:1001274) recruits the "
                    "selenocysteine-specific elongation factor SelB/EEFSEC and Sec-tRNA(Sec) "
                    "to recode an in-frame UGA codon (SO:0000885) during selenocysteine "
                    "incorporation (GO:0001514), cotranslationally inserting L-selenocysteine "
                    "(CHEBI:16633 / MOD:00031) into the nascent selenoprotein."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="SO:1001274",
                        label="SECIS_element",
                        node_type="NUCLEIC_ACID",
                        grounding="SO:1001274",
                        description="Selenocysteine insertion sequence stem-loop RNA element in the selenoprotein mRNA.",
                    ),
                    CausalNodeSpec(
                        node_id="SO:0000885",
                        label="stop_codon_redefined_as_selenocysteine",
                        node_type="NUCLEIC_ACID",
                        grounding="SO:0000885",
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
                        node_id="CHEBI:16633",
                        label="L-selenocysteine",
                        node_type="CHEMICAL",
                        grounding="CHEBI:16633",
                        description="21st amino acid precursor delivered on Sec-tRNA(Sec) to the ribosomal A-site.",
                    ),
                    CausalNodeSpec(
                        node_id="MOD:00031",
                        label="L-selenocysteine residue",
                        node_type="RESIDUE",
                        grounding="MOD:00031",
                        description="Cotranslationally incorporated L-selenocysteine residue in the polypeptide chain.",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="SO:1001274",
                        predicate="RO:0000056",
                        predicate_label="participates in",
                        object="GO:0001514",
                        description="The SECIS RNA stem-loop participates in SelB/EEFSEC recruitment for UGA recoding.",
                        reference="PMID:28192430",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Selenocysteine (Sec) is known as the 21st amino acid, a cysteine analogue "
                            "with selenium replacing sulphur. Sec is inserted co-translationally in a "
                            "small fraction of proteins called selenoproteins."
                        ),
                        notes="SecMarker / selenocysteine incorporation mechanism (PMID:28192430).",
                    ),
                    CausalEdgeSpec(
                        subject="SO:0000885",
                        predicate="RO:0000056",
                        predicate_label="participates in",
                        object="GO:0001514",
                        description="In-frame UGA codon participates as the recoded ribosomal decoding site.",
                        reference="PMID:28192430",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "In selenoprotein genes, the Sec specific tRNA (tRNASec) drives the recoding "
                            "of highly specific UGA codons from stop signals to Sec."
                        ),
                        notes="In-frame UGA codon recoding (PMID:28192430).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0001514",
                        predicate="RO:0002233",
                        predicate_label="has input",
                        object="CHEBI:16633",
                        description="Selenocysteine incorporation consumes Sec-tRNA(Sec)-charged L-selenocysteine.",
                        reference="PMID:28192430",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Sec is inserted co-translationally in a small fraction of proteins called "
                            "selenoproteins. In selenoprotein genes, the Sec specific tRNA (tRNASec) "
                            "drives the recoding of highly specific UGA codons from stop signals to Sec."
                        ),
                        notes="L-selenocysteine substrate input (PMID:28192430).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0001514",
                        predicate="RO:0002234",
                        predicate_label="has output",
                        object="MOD:00031",
                        description="Cotranslational UGA recoding yields an incorporated L-selenocysteine residue in the polypeptide.",
                        reference="PMID:28192430",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "In selenoprotein genes, the Sec specific tRNA (tRNASec) drives the recoding "
                            "of highly specific UGA codons from stop signals to Sec."
                        ),
                        notes="Polypeptide L-selenocysteine residue output (PMID:28192430).",
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
        xrefs=("SO:0001456", "MOD:01187", "CHEBI:21860"),
        evidence=(("PMID:41997725", "Pyrrolysine is synthesized as a free amino acid, charged onto tRNAPyl by pyrrolysyl-tRNA synthetase, and inserted cotranslationally at UAG codons."),),
        detection_methods=(M_PYL,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="pyrrolysine_uag_incorporation",
                label="PylRS/tRNA(Pyl)-mediated cotranslational pyrrolysine incorporation at UAG",
                mechanism_summary=(
                    "Pyrrolysyl-tRNA synthetase activity (GO:0043767 / EC:6.1.1.26) charges "
                    "tRNA(Pyl) with L-pyrrolysine (CHEBI:21860) for pyrrolysine incorporation "
                    "(GO:0030631) at an in-frame UAG amber codon (SO:0000884), inserting an "
                    "L-pyrrolysine residue (MOD:01187) that imparts catalytic functionality."
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
                        node_id="CHEBI:21860",
                        label="L-pyrrolysine",
                        node_type="CHEMICAL",
                        grounding="CHEBI:21860",
                        description="Biosynthesized 22nd amino acid substrate (PylB/PylC/PylD pathway product).",
                    ),
                    CausalNodeSpec(
                        node_id="SO:0000884",
                        label="stop_codon_redefined_as_pyrrolysine",
                        node_type="NUCLEIC_ACID",
                        grounding="SO:0000884",
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
                        node_id="MOD:01187",
                        label="L-pyrrolysine residue",
                        node_type="RESIDUE",
                        grounding="MOD:01187",
                        description="Cotranslationally inserted L-pyrrolysine residue in the methyltransferase polypeptide.",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="GO:0043767",
                        predicate="RO:0002233",
                        predicate_label="has input",
                        object="CHEBI:21860",
                        description="Pyrrolysyl-tRNA synthetase utilizes L-pyrrolysine as aminoacyl substrate.",
                        reference="PMID:41997725",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Pyrrolysine is made as a free amino acid and then used to aminoacylate its "
                            "specific tRNAPyl by pyrrolysyl-tRNAPyl synthetase."
                        ),
                        notes="Pyrrolysine charging by pyrrolysyl-tRNA synthetase (PMID:41997725).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0043767",
                        predicate="RO:0002327",
                        predicate_label="enables",
                        object="GO:0030631",
                        description="Pyrrolysyl-tRNA synthetase activity enables cotranslational pyrrolysine incorporation.",
                        reference="PMID:41997725",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Pyrrolysine is made as a free amino acid and then used to aminoacylate its "
                            "specific tRNAPyl by pyrrolysyl-tRNAPyl synthetase."
                        ),
                        notes="PylRS-enabled pyrrolysine incorporation (PMID:41997725).",
                    ),
                    CausalEdgeSpec(
                        subject="SO:0000884",
                        predicate="RO:0000056",
                        predicate_label="participates in",
                        object="GO:0030631",
                        description="In-frame UAG codon participates as the recoded codon in pyrrolysine incorporation.",
                        reference="PMID:41997725",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "In contrast, local message context stimulates, but is not required for, "
                            "relatively efficient translation of UAG as pyrrolysine."
                        ),
                        notes="In-frame UAG decoding into pyrrolysine residue (PMID:41997725).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0030631",
                        predicate="RO:0002234",
                        predicate_label="has output",
                        object="MOD:01187",
                        description="Pyrrolysine incorporation results in an in-chain L-pyrrolysine residue.",
                        reference="PMID:41997725",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Although many naturally occurring modified amino acids have been identified "
                            "in living organisms, only two, selenocysteine and pyrrolysine, are "
                            "genetically encoded. Each amino acid is inserted cotranslationally into "
                            "proteins imparting catalytic functionality."
                        ),
                        notes="Cotranslationally inserted L-pyrrolysine residue (PMID:41997725).",
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
        xrefs=("MOD:00030", "CHEBI:16552"),
        evidence=(("PMID:42079159", "Peptide deformylase (PDF, EC:3.5.1.88) removes the formyl group from N-formylmethionine (fMet) on nascent peptides."),),
        detection_methods=(M_FMET,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="fmet_initiation_deformylase_bypass",
                label="Methionyl-tRNA formyltransferase initiation and peptide deformylase bypass",
                mechanism_summary=(
                    "Methionyl-tRNA formyltransferase activity (GO:0004479 / EC:2.1.2.9) generates "
                    "N-formyl-L-methionine (CHEBI:16552) on initiator tRNA(fMet) for prokaryotic "
                    "and organellar translational initiation (GO:0006413); when formylmethionine "
                    "deformylase activity (GO:0008463 / EC:3.5.1.88) is bypassed or reduced, the "
                    "N-formyl-L-methionine residue (MOD:00030) is retained at the mature N-terminus."
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
                        node_id="CHEBI:16552",
                        label="N-formyl-L-methionine",
                        node_type="CHEMICAL",
                        grounding="CHEBI:16552",
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
                        description="PDF hydrolase activity (EC:3.5.1.88) that removes the N-formyl group from nascent peptides.",
                    ),
                    CausalNodeSpec(
                        node_id="MOD:00030",
                        label="N-formyl-L-methionine residue",
                        node_type="RESIDUE",
                        grounding="MOD:00030",
                        description="Retained N-terminal N-formyl-L-methionine residue on the polypeptide.",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="GO:0004479",
                        predicate="RO:0002234",
                        predicate_label="has output",
                        object="CHEBI:16552",
                        description="Methionyl-tRNA formyltransferase produces N-formyl-L-methionine on initiator tRNA.",
                        reference="PMID:18718933",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "Because protein synthesis begins with N-formylmethionine in plant "
                            "endosymbiotic organelles, removal of the formyl group by peptide "
                            "deformylase (PDF) is essential to allowing the excision of the first methionine."
                        ),
                        notes="Formylated initiator methionine synthesis (PMID:18718933).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0006413",
                        predicate="RO:0002233",
                        predicate_label="has input",
                        object="CHEBI:16552",
                        description="Translational initiation uses N-formyl-L-methionine as the initiator amino acid.",
                        reference="PMID:18718933",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "Because protein synthesis begins with N-formylmethionine in plant "
                            "endosymbiotic organelles, removal of the formyl group by peptide "
                            "deformylase (PDF) is essential to allowing the excision of the first methionine."
                        ),
                        notes="Translational initiation with fMet (PMID:18718933).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0006413",
                        predicate="RO:0002234",
                        predicate_label="has output",
                        object="MOD:00030",
                        description="Translational initiation deposits an N-formyl-L-methionine residue at the N-terminus of the nascent polypeptide.",
                        reference="PMID:42079159",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "The def gene encodes peptide deformylase (PDF, EC:3.5.1.88), an enzyme "
                            "that contributes to protein processing by removing the formyl group from "
                            "N-formylmethionine (fMet) on nascent peptides."
                        ),
                        notes="Nascent N-terminal fMet residue (PMID:42079159).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0008463",
                        predicate="RO:0002233",
                        predicate_label="has input",
                        object="MOD:00030",
                        description="Formylmethionine deformylase acts on the N-formyl-L-methionine residue of nascent peptides unless bypassed.",
                        reference="PMID:42079159",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "The def gene encodes peptide deformylase (PDF, EC:3.5.1.88), an enzyme "
                            "that contributes to protein processing by removing the formyl group from "
                            "N-formylmethionine (fMet) on nascent peptides."
                        ),
                        notes="PDF deformylation substrate (PMID:42079159).",
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
        xrefs=("MOD:00664", "CHEBI:142417"),
        evidence=(("PMID:30521081", "AdoMet radical epimerases catalyze irreversible L- to D-amino acid transformations in ribosomally synthesized peptides."),),
        detection_methods=(M_DAMINO,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="radical_sam_peptide_epimerization",
                label="Radical-SAM peptide epimerase C-alpha stereoinversion of L- to D-amino acid residues",
                mechanism_summary=(
                    "A radical-SAM peptide aminoacyl-L/D-epimerase (GO:0016855) abstracts the "
                    "alpha-carbon hydrogen atom from a ribosomally translated L-alpha-amino acid "
                    "residue (CHEBI:83228) during protein modification process (GO:0036211) "
                    "and stereoselectively donates a hydrogen atom to the opposite face, "
                    "generating an in-chain D-alpha-amino acid residue (CHEBI:142417)."
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
                        node_id="CHEBI:83228",
                        label="L-alpha-amino acid residue",
                        node_type="RESIDUE",
                        grounding="CHEBI:83228",
                        description="Ribosomally incorporated L-configured alpha-amino acid residue substrate.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0036211",
                        label="protein modification process",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0036211",
                        description="Post-translational C-alpha radical abstraction and stereoinversion.",
                    ),
                    CausalNodeSpec(
                        node_id="CHEBI:142417",
                        label="D-alpha-amino acid residue",
                        node_type="RESIDUE",
                        grounding="CHEBI:142417",
                        description="Post-translationally epimerized D-configured residue in the mature polypeptide.",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="GO:0016855",
                        predicate="RO:0002327",
                        predicate_label="enables",
                        object="GO:0036211",
                        description="Peptide epimerase catalyzes post-translational C-alpha stereoinversion.",
                        reference="PMID:30521081",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "Post-translational modifying enzymes from the S-adenosyl-l-methionine "
                            "(AdoMet) radical superfamily garner attention due to their ability to "
                            "accomplish challenging biochemical reactions. Among them, a family of "
                            "AdoMet radical epimerases catalyze irreversible l- to d-amino acid "
                            "transformations of diverse residues, including 18 sites in the complex "
                            "sponge-derived polytheonamide toxins."
                        ),
                        notes="Radical-SAM peptide epimerase activity (PMID:30521081).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0036211",
                        predicate="RO:0002233",
                        predicate_label="has input",
                        object="CHEBI:83228",
                        description="Ribosomally translated L-alpha-amino acid residue serves as substrate for C-alpha H-abstraction.",
                        reference="PMID:30521081",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "Among them, a family of AdoMet radical epimerases catalyze irreversible "
                            "l- to d-amino acid transformations of diverse residues, including 18 sites "
                            "in the complex sponge-derived polytheonamide toxins."
                        ),
                        notes="L-alpha-amino acid residue substrate (PMID:30521081).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0036211",
                        predicate="RO:0002234",
                        predicate_label="has output",
                        object="CHEBI:142417",
                        description="Back-face hydrogen atom transfer generates an epimerized D-alpha-amino acid residue.",
                        reference="PMID:30521081",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "Introduction of d-amino acids can drastically alter the stability, "
                            "structure, and activity of peptides; thus, epimerases offer opportunities "
                            "in peptide bioengineering."
                        ),
                        notes="Epimerized D-alpha-amino acid residue product (PMID:30521081).",
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
            ("PMID:31665428", "AlloDriver and ASD characterize allosteric regulation induced by ligand binding at a site topographically distinct from an orthosteric site."),
            ("PMID:31707700", "Allosteric mechanisms propagate the effect of ligand binding at one site to a spatially distant orthosteric locus, affecting activity."),
        ),
        detection_methods=(M_FPOCKET,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="allosteric_effector_ensemble_regulation",
                label="Allosteric effector pocket occupancy shifts conformational ensemble to regulate orthosteric activity",
                mechanism_summary=(
                    "An allosteric effector ligand (CHEBI:35224) binds at a topographically distinct "
                    "small molecule binding pocket (GO:0036094), shifting the conformational ensemble "
                    "to enable enzyme regulator activity (GO:0030234) that modulates orthosteric "
                    "catalytic activity (GO:0003824)."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="CHEBI:35224",
                        label="effector",
                        node_type="LIGAND",
                        grounding="CHEBI:35224",
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
                        subject="GO:0036094",
                        predicate="RO:0002233",
                        predicate_label="has input",
                        object="CHEBI:35224",
                        description="Small molecule binding at the topographically distinct regulatory pocket engages the allosteric effector.",
                        reference="PMID:31665428",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Allosteric regulation is one of the most direct and efficient ways to "
                            "fine-tune protein function; it is induced by the binding of a ligand at "
                            "an allosteric site that is topographically distinct from an orthosteric site."
                        ),
                        notes="Allosteric site ligand binding definition (PMID:31665428).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0036094",
                        predicate="RO:0002411",
                        predicate_label="causally upstream of",
                        object="GO:0030234",
                        description="Ligand occupancy at the allosteric pocket propagates a conformational signal across the protein.",
                        reference="PMID:31707700",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "An allosteric mechanism refers to the biological regulation process "
                            "wherein macromolecules propagate the effect of ligand binding at one "
                            "site to a spatially distant orthosteric locus, thus affecting activity."
                        ),
                        notes="Propagation of ligand binding to distant orthosteric site (PMID:31707700).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0030234",
                        predicate="RO:0002211",
                        predicate_label="regulates",
                        object="GO:0003824",
                        description="Allosteric conformational coupling regulates orthosteric catalytic activity.",
                        reference="PMID:31665428",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Allosteric regulation is one of the most direct and efficient ways to "
                            "fine-tune protein function; it is induced by the binding of a ligand at "
                            "an allosteric site that is topographically distinct from an orthosteric site."
                        ),
                        notes="Orthosteric activity regulation via allosteric site (PMID:31665428).",
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
        evidence=(
            ("PMID:31665428", "Allosteric ligand binding at a topographically distinct allosteric site fine-tunes and activates target protein function."),
            ("PMID:31707700", "Ligand binding at an allosteric site propagates conformational changes to a spatially distant orthosteric locus."),
        ),
        detection_methods=(M_FPOCKET,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="allosteric_activator_r_state_stabilization",
                label="Positive allosteric modulator binding stabilizes the active R-state to enhance catalysis",
                mechanism_summary=(
                    "A positive allosteric modulator (CHEBI:35224) binds the activator pocket via "
                    "small molecule binding (GO:0036094), driving enzyme activator activity "
                    "(GO:0008047) that positively regulates orthosteric catalytic activity (GO:0003824)."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="CHEBI:35224",
                        label="effector",
                        node_type="LIGAND",
                        grounding="CHEBI:35224",
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
                        subject="GO:0036094",
                        predicate="RO:0002233",
                        predicate_label="has input",
                        object="CHEBI:35224",
                        description="Small molecule binding at the activator pocket engages the positive allosteric effector.",
                        reference="PMID:31665428",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Allosteric regulation is one of the most direct and efficient ways to "
                            "fine-tune protein function; it is induced by the binding of a ligand at "
                            "an allosteric site that is topographically distinct from an orthosteric site."
                        ),
                        notes="Allosteric activator site ligand engagement (PMID:31665428).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0036094",
                        predicate="RO:0002411",
                        predicate_label="causally upstream of",
                        object="GO:0008047",
                        description="Activator pocket occupancy propagates an activating conformational change to the orthosteric site.",
                        reference="PMID:31707700",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "An allosteric mechanism refers to the biological regulation process "
                            "wherein macromolecules propagate the effect of ligand binding at one "
                            "site to a spatially distant orthosteric locus, thus affecting activity."
                        ),
                        notes="Allosteric propagation to enzyme activation (PMID:31707700).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0008047",
                        predicate="RO:0002213",
                        predicate_label="positively regulates",
                        object="GO:0003824",
                        description="Enzyme activator activity increases orthosteric catalytic turnover or substrate affinity.",
                        reference="PMID:31665428",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Allosteric regulation is one of the most direct and efficient ways to "
                            "fine-tune protein function; it is induced by the binding of a ligand at "
                            "an allosteric site that is topographically distinct from an orthosteric site."
                        ),
                        notes="Positive regulation of catalytic activity (PMID:31665428).",
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
        evidence=(
            ("PMID:31665428", "Allosteric ligand binding at a topographically distinct site modulates and inhibits target protein function."),
            ("PMID:31707700", "Allosteric ligand binding propagates regulatory effects to a spatially distant orthosteric locus."),
        ),
        detection_methods=(M_FPOCKET,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="allosteric_inhibitor_t_state_stabilization",
                label="Negative allosteric modulator binding stabilizes the T-state to inhibit catalysis",
                mechanism_summary=(
                    "A negative allosteric modulator or feedback inhibitor (CHEBI:35224) binds at "
                    "the allosteric inhibitor pocket via small molecule binding (GO:0036094), "
                    "mediating enzyme inhibitor activity (GO:0004857) that negatively regulates "
                    "orthosteric catalytic activity (GO:0003824)."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="CHEBI:35224",
                        label="effector",
                        node_type="LIGAND",
                        grounding="CHEBI:35224",
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
                        subject="GO:0036094",
                        predicate="RO:0002233",
                        predicate_label="has input",
                        object="CHEBI:35224",
                        description="Small molecule binding at the allosteric inhibitor pocket engages the negative effector.",
                        reference="PMID:31665428",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Allosteric regulation is one of the most direct and efficient ways to "
                            "fine-tune protein function; it is induced by the binding of a ligand at "
                            "an allosteric site that is topographically distinct from an orthosteric site."
                        ),
                        notes="Allosteric inhibitor pocket ligand engagement (PMID:31665428).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0036094",
                        predicate="RO:0002411",
                        predicate_label="causally upstream of",
                        object="GO:0004857",
                        description="Inhibitor pocket occupancy propagates an inhibitory conformational signal to the orthosteric site.",
                        reference="PMID:31707700",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "An allosteric mechanism refers to the biological regulation process "
                            "wherein macromolecules propagate the effect of ligand binding at one "
                            "site to a spatially distant orthosteric locus, thus affecting activity."
                        ),
                        notes="Allosteric propagation to enzyme inhibition (PMID:31707700).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0004857",
                        predicate="RO:0002212",
                        predicate_label="negatively regulates",
                        object="GO:0003824",
                        description="Allosteric enzyme inhibitor activity non-competitively attenuates orthosteric catalysis.",
                        reference="PMID:31665428",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Allosteric regulation is one of the most direct and efficient ways to "
                            "fine-tune protein function; it is induced by the binding of a ligand at "
                            "an allosteric site that is topographically distinct from an orthosteric site."
                        ),
                        notes="Negative regulation of catalytic activity (PMID:31665428).",
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
        evidence=(
            ("PMID:42734533", "Cryptic pockets are transient ligand-binding sites that remain hidden in apo protein structures and become accessible only through conformational change."),
            ("PMID:42821008", "Allosteric and cryptic binding pockets offer routes to modulate biological targets historically considered undruggable."),
        ),
        detection_methods=(M_FPOCKET,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="cryptic_pocket_opening_and_capture",
                label="Conformational fluctuation opens transient cryptic cavity for ligand capture and allosteric regulation",
                mechanism_summary=(
                    "Thermal loop/side-chain fluctuations expose a transient small molecule binding "
                    "cavity (GO:0036094) that captures an effector ligand (CHEBI:35224), stabilizing "
                    "the open-pocket state to enable enzyme regulator activity (GO:0030234) on "
                    "orthosteric catalytic activity (GO:0003824)."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="CHEBI:35224",
                        label="effector",
                        node_type="LIGAND",
                        grounding="CHEBI:35224",
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
                        subject="GO:0036094",
                        predicate="RO:0002233",
                        predicate_label="has input",
                        object="CHEBI:35224",
                        description="Small molecule binding at the transiently exposed cryptic pocket captures the effector ligand.",
                        reference="PMID:42734533",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Cryptic pockets are transient ligand-binding sites that remain hidden "
                            "in apo protein structures and become accessible only through "
                            "conformational change, making them difficult to identify and exploit "
                            "in structure-based ligand discovery."
                        ),
                        notes="Cryptic pocket opening and ligand binding (PMID:42734533).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0036094",
                        predicate="RO:0002411",
                        predicate_label="causally upstream of",
                        object="GO:0030234",
                        description="Ligand capture in the open cryptic pocket stabilizes a regulatory conformational state.",
                        reference="PMID:42734533",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Cryptic pockets are transient ligand-binding sites that remain hidden "
                            "in apo protein structures and become accessible only through "
                            "conformational change, making them difficult to identify and exploit "
                            "in structure-based ligand discovery."
                        ),
                        notes="Cryptic pocket conformational capture (PMID:42734533).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0030234",
                        predicate="RO:0002211",
                        predicate_label="regulates",
                        object="GO:0003824",
                        description="Cryptic-pocket-mediated enzyme regulator activity modulates target catalytic activity.",
                        reference="PMID:42821008",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Allosteric and cryptic binding pockets represent a vast underexploited "
                            "frontier in drug discovery, offering routes to biological targets "
                            "historically considered undruggable."
                        ),
                        notes="Modulation of target activity via cryptic pockets (PMID:42821008).",
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
        evidence=(
            ("PMID:42628823", "Interface-localized pockets across oligomeric enzyme ensembles serve as candidate regulatory regions for allosteric modulation."),
            ("PMID:42539251", "Post-binding conformational changes across the dimer interface regulate substrate cleavage across active sites."),
        ),
        detection_methods=(M_FPOCKET,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="inter_protomer_allosteric_cooperativity",
                label="Inter-subunit effector binding couples quaternary interface rearrangement to cooperative catalysis",
                mechanism_summary=(
                    "An effector (CHEBI:35224) binds via small molecule binding (GO:0036094) at "
                    "an oligomeric subunit boundary mediated by protein homodimerization activity "
                    "(GO:0042803), driving enzyme regulator activity (GO:0030234) that cooperatively "
                    "modulates catalytic activity (GO:0003824) across protomers."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="CHEBI:35224",
                        label="effector",
                        node_type="LIGAND",
                        grounding="CHEBI:35224",
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
                        subject="GO:0036094",
                        predicate="RO:0002233",
                        predicate_label="has input",
                        object="CHEBI:35224",
                        description="Small molecule binding at the inter-subunit cavity engages the allosteric effector.",
                        reference="PMID:42628823",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Solvent mapping using FTMap and FTMove across oligomeric ensembles "
                            "revealed multiple high-confidence cavities predominantly located at "
                            "subunit interfaces, in addition to canonical catalytic sites."
                        ),
                        notes="Inter-subunit cavity detection across oligomeric ensembles (PMID:42628823).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0036094",
                        predicate="RO:0002211",
                        predicate_label="regulates",
                        object="GO:0042803",
                        description="Interface pocket occupancy modulates subunit-subunit packing geometry.",
                        reference="PMID:42628823",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Across all four enzymes, interface-localized pockets consistently "
                            "emerged as promising candidate regulatory regions, suggesting that "
                            "protein-protein interfaces may represent valuable targets for "
                            "allosteric modulation."
                        ),
                        notes="Protein-protein interface pockets as allosteric regulatory regions (PMID:42628823).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0042803",
                        predicate="RO:0002411",
                        predicate_label="causally upstream of",
                        object="GO:0030234",
                        description="Conformational changes across the dimer interface propagate allosteric regulation between protomers.",
                        reference="PMID:42539251",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "Consistent with the conformational asymmetry observed in apo -FraB "
                            "crystal structures, our findings establish a half-site reactivity "
                            "mechanism in which post-binding conformational changes across the "
                            "dimer interface restrict substrate cleavage to one active site even "
                            "though both protomers are able to bind substrate."
                        ),
                        notes="Dimer interface conformational coupling (PMID:42539251).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0030234",
                        predicate="RO:0002211",
                        predicate_label="regulates",
                        object="GO:0003824",
                        description="Cooperative quaternary transition regulates catalytic activity across protomers.",
                        reference="PMID:42628823",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Across all four enzymes, interface-localized pockets consistently "
                            "emerged as promising candidate regulatory regions, suggesting that "
                            "protein-protein interfaces may represent valuable targets for "
                            "allosteric modulation."
                        ),
                        notes="Cooperative catalytic regulation across subunit interfaces (PMID:42628823).",
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
                    "An N-terminal signal_peptide (SO:0000418) participates in "
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
                        predicate="RO:0000056",
                        predicate_label="participates in",
                        object="GO:0043952",
                        description="The tripartite Sec/SPI signal peptide targets the preprotein to the SecYEG/Sec61 translocon.",
                        reference="PMID:34980915",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Signal peptides (SPs) are short N-terminal amino acid sequences that "
                            "control protein secretion and translocation in all living organisms."
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
                        snippet="SPs can be cleaved off after the protein has been translocated across the membrane.",
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
                            "Signal peptides (SPs) are short N-terminal amino acid sequences that "
                            "control protein secretion and translocation in all living organisms."
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
        evidence=(
            ("PMID:34980915", "SignalP 6.0 predicts all five types of signal peptides and cleavage sites across organisms."),
            ("PMID:42050317", "Nascent bacterial lipoproteins are sequentially modified by Lgt, cleaved by LspA (signal peptidase II), and N-acylated."),
        ),
        detection_methods=(M_SIGNALP6,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="sec_spii_lipobox_diacylglyceryl_cleavage",
                label="Sec translocation, Lgt lipobox S-diacylglycerylation, and LspA signal peptidase II cleavage",
                mechanism_summary=(
                    "A lipobox signal_peptide (SO:0000418) participates in protein transport by the Sec "
                    "complex (GO:0043952), after which Lgt catalyzes protein lipidation (GO:0006497) "
                    "of the invariant +1 cysteine to S-diacylglycerol-L-cysteine (MOD:00116), "
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
                        node_id="MOD:00116",
                        label="S-diacylglycerol-L-cysteine",
                        node_type="PTM",
                        grounding="MOD:00116",
                        description="Mature N-terminal S-diacylglyceryl-modified cysteine membrane anchor.",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="SO:0000418",
                        predicate="RO:0000056",
                        predicate_label="participates in",
                        object="GO:0043952",
                        description="The Sec/SPII leader directs the prolipoprotein across the Sec translocon.",
                        reference="PMID:34980915",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Signal peptides (SPs) are short N-terminal amino acid sequences that "
                            "control protein secretion and translocation in all living organisms."
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
                        snippet="SPs can be cleaved off after the protein has been translocated across the membrane.",
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
                            "In this work, we present SignalP 6.0, a machine learning model that detects "
                            "all five known types of SPs and is applicable to all organisms, including "
                            "metagenomic data. By using protein language models, SignalP 6.0 is able to "
                            "predict types of SPs with limited training data, extrapolate to distantly "
                            "related organisms and, without using explicit region annotation, identify "
                            "the regions of SPs."
                        ),
                        notes="SPase II cleavage requires prior lipobox lipidation (PMID:34980915).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0004175",
                        predicate="RO:0002234",
                        predicate_label="has output",
                        object="MOD:00116",
                        description="SPase II cleavage exposes S-diacylglycerol-L-cysteine as the new N-terminal residue.",
                        reference="PMID:34980915",
                        evidence_code="ECO:0000305",
                        snippet="SPs can be cleaved off after the protein has been translocated across the membrane.",
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
        evidence=(
            ("PMID:34980915", "Prediction of Tat/SPI twin-arginine signal peptides with SignalP 6.0."),
            ("PMID:34122494", "Secretory (Sec) and twin-arginine translocation (Tat) signal peptides direct protein export across membranes."),
        ),
        detection_methods=(M_SIGNALP6,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="tat_spi_folded_export_and_cleavage",
                label="Twin-arginine (TatABC) folded protein translocation and signal peptidase I cleavage",
                mechanism_summary=(
                    "A twin-arginine signal_peptide (SO:0000418) participates in "
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
                        predicate="RO:0000056",
                        predicate_label="participates in",
                        object="GO:0043953",
                        description="The twin-arginine motif targets folded preproteins to the Tat translocase.",
                        reference="PMID:34122494",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "We developed a set of in-house expression vectors for transient transformation "
                            "of Nicotiana benthamiana leaves that target a VHH-Fc to the thylakoid lumen via "
                            "either secretory (Sec) or twin-arginine translocation (Tat) import pathways."
                        ),
                        notes="Twin-arginine targeting to Tat translocon (PMID:34122494).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0043953",
                        predicate="RO:0002411",
                        predicate_label="causally upstream of",
                        object="GO:0004175",
                        description="Tat translocation exposes the c-region cleavage site to signal peptidase I.",
                        reference="PMID:34980915",
                        evidence_code="ECO:0000305",
                        snippet="SPs can be cleaved off after the protein has been translocated across the membrane.",
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
                            "Signal peptides (SPs) are short N-terminal amino acid sequences that "
                            "control protein secretion and translocation in all living organisms."
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
        evidence=(
            ("PMID:34980915", "Identification of Tat/SPII twin-arginine lipoprotein signal peptides by SignalP 6.0."),
            ("PMID:26341016", "Involvement of Sec-, Tat- and SRP-dependent protein targeting pathways in bacterial membranes."),
        ),
        detection_methods=(M_SIGNALP6,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="tat_spii_folded_lipoprotein_processing",
                label="Tat translocation of folded prolipoprotein followed by lipobox lipidation and SPase II cleavage",
                mechanism_summary=(
                    "A Tat/SPII signal_peptide (SO:0000418) participates in folded prolipoprotein export "
                    "via protein transport by the Tat complex (GO:0043953), followed by Lgt-mediated "
                    "protein lipidation (GO:0006497) and LspA endopeptidase activity (GO:0004175) "
                    "yielding an N-terminal S-diacylglycerol-L-cysteine (MOD:00116)."
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
                        node_id="MOD:00116",
                        label="S-diacylglycerol-L-cysteine",
                        node_type="PTM",
                        grounding="MOD:00116",
                        description="Mature N-terminal lipid-anchored cysteine residue.",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="SO:0000418",
                        predicate="RO:0000056",
                        predicate_label="participates in",
                        object="GO:0043953",
                        description="The Tat/SPII leader targets folded prolipoproteins to the Tat translocon.",
                        reference="PMID:26341016",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "The involvement of Sec-, Tat- and signal recognition particle- (SRP)-dependent "
                            "protein targeting pathways is discussed, together with the possible involvement "
                            "of a so-called 'spontaneous' pathway for the insertion of membrane proteins, "
                            "previously characterised for chloroplast thylakoid membrane proteins."
                        ),
                        notes="Tat translocation of Tat/SPII prolipoproteins (PMID:26341016).",
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
                            "In this work, we present SignalP 6.0, a machine learning model that detects "
                            "all five known types of SPs and is applicable to all organisms, including "
                            "metagenomic data."
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
                        snippet="SPs can be cleaved off after the protein has been translocated across the membrane.",
                        notes="SPase II cleavage of Tat/SPII leader (PMID:34980915).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0004175",
                        predicate="RO:0002234",
                        predicate_label="has output",
                        object="MOD:00116",
                        description="SPase II cleavage yields the mature N-terminal S-diacylglycerol-L-cysteine anchor.",
                        reference="PMID:34980915",
                        evidence_code="ECO:0000305",
                        snippet="SPs can be cleaved off after the protein has been translocated across the membrane.",
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
                    "A short basic prepilin signal_peptide (SO:0000418) participates in inner-membrane "
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
                        predicate="RO:0000056",
                        predicate_label="participates in",
                        object="GO:0043952",
                        description="The Sec/SPIII leader directs Sec-dependent membrane insertion of the prepilin.",
                        reference="PMID:34980915",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Signal peptides (SPs) are short N-terminal amino acid sequences that "
                            "control protein secretion and translocation in all living organisms."
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
                        snippet="SPs can be cleaved off after the protein has been translocated across the membrane.",
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
                            "In this work, we present SignalP 6.0, a machine learning model that detects "
                            "all five known types of SPs and is applicable to all organisms, including "
                            "metagenomic data."
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
        xrefs=("SO:0001808",),
        evidence=(("PMID:36173160", "Tom20 recognizes the mitochondrial targeting signal in N-terminal presequences to sort proteins into the mitochondrial matrix."),),
        detection_methods=(M_TARGETP2,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="mtp_tom_tim23_import_mpp_cleavage",
                label="TOM/TIM23 mitochondrial matrix import and MPP presequence cleavage",
                mechanism_summary=(
                    "An N-terminal mitochondrial_targeting_signal (SO:0001808) participates in protein "
                    "import into mitochondrial matrix (GO:0030150) across the TOM and TIM23 "
                    "translocons, causally upstream of mitochondrial processing peptidase endopeptidase "
                    "activity (GO:0004175) with target end location in the mitochondrial matrix (GO:0005759)."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="SO:0001808",
                        label="mitochondrial_targeting_signal",
                        node_type="MOTIF",
                        grounding="SO:0001808",
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
                        node_id="GO:0004175",
                        label="endopeptidase activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0004175",
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
                        subject="SO:0001808",
                        predicate="RO:0000056",
                        predicate_label="participates in",
                        object="GO:0030150",
                        description="The amphipathic N-terminal presequence is recognized by Tom20 to initiate matrix import.",
                        reference="PMID:36173160",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "The 20-kDa TOM (translocase of outer mitochondrial membrane) subunit, Tom20, "
                            "is the first receptor of the protein import pathway into mitochondria. Tom20 "
                            "recognizes the mitochondrial targeting signal embedded in the presequences "
                            "attached to mature mitochondrial proteins, as an N-terminal extension."
                        ),
                        notes="mTP recognition by Tom20 for mitochondrial matrix import (PMID:36173160).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0030150",
                        predicate="RO:0002411",
                        predicate_label="causally upstream of",
                        object="GO:0004175",
                        description="Translocation into the matrix exposes the presequence attached to mature mitochondrial proteins for cleavage.",
                        reference="PMID:36173160",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "Tom20 recognizes the mitochondrial targeting signal embedded in the presequences "
                            "attached to mature mitochondrial proteins, as an N-terminal extension. "
                            "Consequently, ~1,000 different mitochondrial proteins are sorted into the "
                            "mitochondrial matrix, and distinguished from non-mitochondrial proteins."
                        ),
                        notes="Presequence processing upon mitochondrial matrix import (PMID:36173160).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0030150",
                        predicate="RO:0002339",
                        predicate_label="has target end location",
                        object="GO:0005759",
                        description="Mitochondrial matrix import delivers sorted proteins into the mitochondrial matrix.",
                        reference="PMID:36173160",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "Consequently, ~1,000 different mitochondrial proteins are sorted into the "
                            "mitochondrial matrix, and distinguished from non-mitochondrial proteins."
                        ),
                        notes="Target end location in the mitochondrial matrix (PMID:36173160).",
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
        xrefs=("SO:0000725",),
        evidence=(("PMID:37324391", "Chloroplast transit peptides direct import across the outer and inner envelope membranes and are cleaved by stromal processing peptidase."),),
        detection_methods=(M_TARGETP2,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="ctp_toc_tic_stromal_import_spp_cleavage",
                label="TOC/TIC chloroplast stromal import and stromal processing peptidase (SPP) cleavage",
                mechanism_summary=(
                    "A chloroplast transit_peptide (SO:0000725) participates in protein import into "
                    "chloroplast stroma (GO:0045037) across the outer and inner envelope translocons, "
                    "causally upstream of stromal processing peptidase endopeptidase activity (GO:0004175) "
                    "with target end location in the chloroplast stroma (GO:0009570)."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="SO:0000725",
                        label="transit_peptide",
                        node_type="MOTIF",
                        grounding="SO:0000725",
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
                        subject="SO:0000725",
                        predicate="RO:0000056",
                        predicate_label="participates in",
                        object="GO:0045037",
                        description="The N-terminal cTP directs precursor translocation through the chloroplast envelope import machinery.",
                        reference="PMID:37324391",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Transit peptides contain specific motifs and domains initially recognized by "
                            "cytosolic factors followed by the chloroplast import components at the outer "
                            "and inner envelope of the chloroplast membrane."
                        ),
                        notes="cTP-mediated import into chloroplast stroma (PMID:37324391).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0045037",
                        predicate="RO:0002411",
                        predicate_label="causally upstream of",
                        object="GO:0004175",
                        description="Import into the stroma exposes the cTP cleavage site to stromal processing peptidase (SPP).",
                        reference="PMID:37324391",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Once the preprotein emerges on the stromal side of the chloroplast protein "
                            "import machinery, the transit peptide is cleaved by stromal processing peptidase."
                        ),
                        notes="SPP cleavage upon stromal import (PMID:37324391).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0045037",
                        predicate="RO:0002339",
                        predicate_label="has target end location",
                        object="GO:0009570",
                        description="Chloroplast stromal import delivers the preprotein to the stromal side of the import machinery.",
                        reference="PMID:37324391",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Once the preprotein emerges on the stromal side of the chloroplast protein "
                            "import machinery, the transit peptide is cleaved by stromal processing peptidase."
                        ),
                        notes="Target end location in the chloroplast stroma (PMID:37324391).",
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
        xrefs=("SO:0000725",),
        evidence=(("PMID:37324391", "Cleavage of chloroplast transit peptides exposes a second targeting signal guiding thylakoid-localized proteins to the thylakoid lumen."),),
        detection_methods=(M_TARGETP2,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="lutp_bipartite_stromal_thylakoid_import",
                label="Bipartite stromal TOC/TIC import, SPP intermediate cleavage, and thylakoid Sec/Tat + TPP processing",
                mechanism_summary=(
                    "A bipartite transit_peptide (SO:0000725) first participates in protein "
                    "import into chloroplast stroma (GO:0045037) and SPP cleavage, exposing the "
                    "second targeting signal for protein import into chloroplast thylakoid "
                    "membrane (GO:0045038), TPP endopeptidase activity (GO:0004175), and localization "
                    "to the chloroplast thylakoid lumen (GO:0009543)."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="SO:0000725",
                        label="transit_peptide",
                        node_type="MOTIF",
                        grounding="SO:0000725",
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
                        description="Stromal and thylakoidal processing peptidase cleavage of the bipartite transit peptide.",
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
                        subject="SO:0000725",
                        predicate="RO:0000056",
                        predicate_label="participates in",
                        object="GO:0045037",
                        description="The N-terminal stromal targeting portion of the bipartite luTP directs chloroplast envelope import.",
                        reference="PMID:37324391",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Transit peptides contain specific motifs and domains initially recognized by "
                            "cytosolic factors followed by the chloroplast import components at the outer "
                            "and inner envelope of the chloroplast membrane."
                        ),
                        notes="First-stage stromal import of bipartite luTP (PMID:37324391).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0045037",
                        predicate="RO:0002411",
                        predicate_label="causally upstream of",
                        object="GO:0045038",
                        description="Stromal import and transit peptide cleavage expose a second targeting signal for thylakoid translocation.",
                        reference="PMID:37324391",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "In the case of thylakoid-localized proteins, cleavage of the transit peptides "
                            "may expose a second targeting signal guiding the protein to the thylakoid lumen "
                            "or allow insertion into the thylakoid membrane by internal sequence information."
                        ),
                        notes="Unmasking of second targeting signal after stromal import (PMID:37324391).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0045038",
                        predicate="RO:0002411",
                        predicate_label="causally upstream of",
                        object="GO:0004175",
                        description="Cleavage of the transit peptide accompanies thylakoid sorting.",
                        reference="PMID:37324391",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Once the preprotein emerges on the stromal side of the chloroplast protein "
                            "import machinery, the transit peptide is cleaved by stromal processing peptidase."
                        ),
                        notes="Processing peptidase cleavage during plastid/thylakoid sorting (PMID:37324391).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0045038",
                        predicate="RO:0002339",
                        predicate_label="has target end location",
                        object="GO:0009543",
                        description="The second targeting signal guides thylakoid-localized proteins to the thylakoid lumen.",
                        reference="PMID:37324391",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "In the case of thylakoid-localized proteins, cleavage of the transit peptides "
                            "may expose a second targeting signal guiding the protein to the thylakoid lumen "
                            "or allow insertion into the thylakoid membrane by internal sequence information."
                        ),
                        notes="Target end location in the chloroplast thylakoid lumen (PMID:37324391).",
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
        evidence=(
            ("PMID:31557781", "Cathepsin C is synthesized as an inactive zymogen with a propeptide that is processed into the mature active enzyme by proteolytic cleavages."),
            ("PMID:38421254", "Preparation of active enzyme requires post-translational proteolytic digestion of the zymogen propeptide."),
        ),
        detection_methods=(M_PROPEP,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="zymogen_propeptide_autoinhibition_and_activation",
                label="Autoinhibitory propeptide steric blockade and proteolytic zymogen activation",
                mechanism_summary=(
                    "An uncleaved propeptide (SO:0001062) participates in zymogen activation (GO:0031638) "
                    "while intramolecular enzyme inhibitor activity (GO:0004857) negatively regulates "
                    "catalytic activity (GO:0003824); endopeptidase activity (GO:0004175) enables "
                    "zymogen activation (GO:0031638), positively regulating catalytic activity."
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
                        predicate="RO:0000056",
                        predicate_label="participates in",
                        object="GO:0031638",
                        description="The intramolecular propeptide of the inactive zymogen is processed during zymogen activation.",
                        reference="PMID:31557781",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "CatC is first synthetized as an inactive zymogen containing an intramolecular "
                            "chain propeptide, the dimeric form of which is processed into the mature "
                            "tetrameric form by proteolytic cleavages."
                        ),
                        notes="Intramolecular propeptide processing during zymogen maturation (PMID:31557781).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0004857",
                        predicate="RO:0002212",
                        predicate_label="negatively regulates",
                        object="GO:0003824",
                        description="Intramolecular propeptide inhibition maintains the zymogen in an inactive state.",
                        reference="PMID:31557781",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "CatC is first synthetized as an inactive zymogen containing an intramolecular "
                            "chain propeptide, the dimeric form of which is processed into the mature "
                            "tetrameric form by proteolytic cleavages."
                        ),
                        notes="Negative regulation of catalysis in latent zymogen (PMID:31557781).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0004175",
                        predicate="RO:0002327",
                        predicate_label="enables",
                        object="GO:0031638",
                        description="Post-translational proteolytic digestion of the propeptide triggers zymogen activation.",
                        reference="PMID:38421254",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "The preparation of active recombinant MTG requires post-translational "
                            "proteolytic digestion of a propeptide that functions as an intramolecular "
                            "chaperone to assist the correct folding of the MTG zymogen (MTGz) in the biosynthesis."
                        ),
                        notes="Proteolytic cleavage drives zymogen activation (PMID:38421254).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0031638",
                        predicate="RO:0002213",
                        predicate_label="positively regulates",
                        object="GO:0003824",
                        description="Proteolytic removal of the propeptide produces the active mature enzyme.",
                        reference="PMID:38421254",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "The preparation of active recombinant MTG requires post-translational "
                            "proteolytic digestion of a propeptide that functions as an intramolecular "
                            "chaperone to assist the correct folding of the MTG zymogen (MTGz) in the biosynthesis."
                        ),
                        notes="Unmasking of mature catalytic activity (PMID:38421254).",
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
        evidence=(("PMID:33569954", "Subtilisin N-terminal propeptide acts as an intramolecular chaperone (IMC) for domain folding before cleavage and IMC degradation."),),
        detection_methods=(M_PROPEP,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="imc_propeptide_folding_and_autocleavage",
                label="Intramolecular-chaperone propeptide catalyzes protease domain folding followed by autoprocessing",
                mechanism_summary=(
                    "An intramolecular-chaperone propeptide (SO:0001062) participates in protein folding "
                    "(GO:0006457) of the cognate protease domain, which then undergoes rate-limiting "
                    "endopeptidase activity (GO:0004175) cleavage and IMC degradation during zymogen "
                    "activation (GO:0031638)."
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
                        predicate="RO:0000056",
                        predicate_label="participates in",
                        object="GO:0006457",
                        description="The N-terminal IMC propeptide chaperones the folding of the subtilisin domain.",
                        reference="PMID:33569954",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "Subtilisin is produced as a precursor that requires its N-terminal propeptide "
                            "to act as an IMC to chaperone the folding of its subtilisin domain."
                        ),
                        notes="Intramolecular chaperone role in protein folding (PMID:33569954).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0006457",
                        predicate="RO:0002411",
                        predicate_label="causally upstream of",
                        object="GO:0004175",
                        description="During precursor folding, the peptide bond between the IMC and subtilisin domain is cleaved.",
                        reference="PMID:33569954",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "During the precursor folding, the cleavage of the peptide bond between the IMC "
                            "and the subtilisin domain is the most important and rate-limiting step, which "
                            "leads to the structural reorganization of the subtilisin domain and IMC's degradation."
                        ),
                        notes="Precursor folding enables rate-limiting IMC cleavage (PMID:33569954).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0004175",
                        predicate="RO:0002411",
                        predicate_label="causally upstream of",
                        object="GO:0031638",
                        description="Cleavage and degradation of the IMC propeptide completes structural reorganization and activation.",
                        reference="PMID:33569954",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "During the precursor folding, the cleavage of the peptide bond between the IMC "
                            "and the subtilisin domain is the most important and rate-limiting step, which "
                            "leads to the structural reorganization of the subtilisin domain and IMC's degradation."
                        ),
                        notes="IMC degradation completes enzyme activation (PMID:33569954).",
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
        evidence=(
            ("PMID:37721936", "Precursor proteins are N-terminally cleaved at dibasic sites matching the consensus for furin and subtilisin/kexin (PCSK) proprotein convertases."),
            ("PMID:37482809", "Kex2 serine protease catalyzes proteolytic maturation of secretory proteins by cleaving after dibasic residues in the late Golgi network."),
        ),
        detection_methods=(M_PROPEP,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="dibasic_propeptide_convertase_excision",
                label="Proprotein convertase cleavage at dibasic (KR/RR/RxxR) motifs excises propeptide for hormone maturation",
                mechanism_summary=(
                    "A dibasic-flanked propeptide (SO:0001062) participates in proteolytic "
                    "protein processing (GO:0016485) enabled by subtilisin/kexin-like "
                    "proprotein convertase endopeptidase activity (GO:0004175), driving secretory "
                    "protein maturation (GO:0051604)."
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
                        description="Proprotein convertase (PCSK/furin/Kex2) cleavage C-terminal to basic pairs.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0016485",
                        label="protein processing",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0016485",
                        description="Endoproteolytic propeptide excision in the late Golgi network or secretory granules.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0051604",
                        label="protein maturation",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0051604",
                        description="Proteolytic maturation of secretory proteins.",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="SO:0001062",
                        predicate="RO:0000056",
                        predicate_label="participates in",
                        object="GO:0016485",
                        description="The dibasic-flanked N-terminal propeptide is cleaved at the consensus furin/PCSK dibasic site.",
                        reference="PMID:37721936",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "Some types of collagens, including transmembrane MACIT collagens and C. elegans "
                            "cuticle collagens, are N-terminally cleaved at a dibasic site that resembles the "
                            "consensus for furin or other proprotein convertases of the subtilisin/kexin (PCSK) family."
                        ),
                        notes="Dibasic site cleavage by PCSK/furin convertases (PMID:37721936).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0004175",
                        predicate="RO:0002327",
                        predicate_label="enables",
                        object="GO:0016485",
                        description="Subtilisin/kexin serine protease activity cleaves after dibasic residues in the late Golgi network.",
                        reference="PMID:37482809",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "Kex2 protease (Kex2p) is a membrane-bound serine protease responsible for the "
                            "proteolytic maturation of various secretory proteins by cleaving after dibasic "
                            "residues in the late Golgi network."
                        ),
                        notes="Endoproteolytic cleavage after dibasic residues (PMID:37482809).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0016485",
                        predicate="RO:0002411",
                        predicate_label="causally upstream of",
                        object="GO:0051604",
                        description="Proteolytic cleavage after dibasic residues drives maturation of secretory proteins.",
                        reference="PMID:37482809",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "Kex2 protease (Kex2p) is a membrane-bound serine protease responsible for the "
                            "proteolytic maturation of various secretory proteins by cleaving after dibasic "
                            "residues in the late Golgi network."
                        ),
                        notes="Proteolytic maturation of secretory proteins (PMID:37482809).",
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
        evidence=(
            (
                "PMID:42829235",
                "Protein disulfide isomerase catalyzes intramolecular disulfide bond formation during oxidative protein folding.",
            ),
        ),
        detection_methods=(M_DSSP_SSBOND,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="intrachain_disulfide_oxidative_folding",
                label="Oxidative thiol-disulfide crosslinking of intrachain cysteines stabilizes tertiary protein folding",
                mechanism_summary=(
                    "Protein disulfide isomerase activity (GO:0003756) oxidizes paired L-cysteine "
                    "residues (CHEBI:29950) within the same polypeptide chain to form an intrachain "
                    "L-cystine (cross-link) (MOD:00034), positively regulating tertiary protein "
                    "folding (GO:0006457)."
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
                        description="Thermodynamic stabilization of native tertiary structure via intramolecular disulfide formation.",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="GO:0003756",
                        predicate="RO:0002233",
                        predicate_label="has input",
                        object="CHEBI:29950",
                        description="Protein disulfide isomerase oxidizes paired intrachain L-cysteine thiolates.",
                        reference="PMID:42829235",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "Here, we developed an expression system for recombinant human serum "
                            "albumin (rHSA) by fusing the a domain of human protein disulfide "
                            "isomerase (PDI) to the N-terminus of HSA. PDI(a)-mediated cis-fusion "
                            "enabled high-level production of soluble rHSA in oxidizing E. coli "
                            "strains under low-temperature conditions. Purified E. coli-rHSA was "
                            "predominantly monomeric and had the molecular mass expected for HSA "
                            "containing 17 intramolecular disulfide bonds."
                        ),
                        notes="Oxidation of paired intrachain cysteine residues by PDI (PMID:42829235).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0003756",
                        predicate="RO:0002234",
                        predicate_label="has output",
                        object="MOD:00034",
                        description="Oxidative thiol coupling yields covalent intramolecular L-cystine crosslinks.",
                        reference="PMID:42829235",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "Here, we developed an expression system for recombinant human serum "
                            "albumin (rHSA) by fusing the a domain of human protein disulfide "
                            "isomerase (PDI) to the N-terminus of HSA. PDI(a)-mediated cis-fusion "
                            "enabled high-level production of soluble rHSA in oxidizing E. coli "
                            "strains under low-temperature conditions. Purified E. coli-rHSA was "
                            "predominantly monomeric and had the molecular mass expected for HSA "
                            "containing 17 intramolecular disulfide bonds."
                        ),
                        notes="Formation of intramolecular cystine crosslinks (PMID:42829235).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0003756",
                        predicate="RO:0002213",
                        predicate_label="positively regulates",
                        object="GO:0006457",
                        description="PDI-catalyzed intramolecular disulfide bond formation promotes soluble monomeric protein folding.",
                        reference="PMID:42829235",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "Here, we developed an expression system for recombinant human serum "
                            "albumin (rHSA) by fusing the a domain of human protein disulfide "
                            "isomerase (PDI) to the N-terminus of HSA. PDI(a)-mediated cis-fusion "
                            "enabled high-level production of soluble rHSA in oxidizing E. coli "
                            "strains under low-temperature conditions. Purified E. coli-rHSA was "
                            "predominantly monomeric and had the molecular mass expected for HSA "
                            "containing 17 intramolecular disulfide bonds."
                        ),
                        notes="Intramolecular disulfide formation promotes soluble folding (PMID:42829235).",
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
        evidence=(
            (
                "PMID:19005088",
                "Available cysteine residues in folded monomers form interchain disulfide bonds with cysteine residues in companion subunits.",
            ),
        ),
        detection_methods=(M_DSSP_SSBOND,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="interchain_disulfide_quaternary_crosslinking",
                label="Inter-subunit cystine crosslinking covalently stabilizes quaternary dimer/oligomer assembly",
                mechanism_summary=(
                    "Protein disulfide isomerase activity (GO:0003756) oxidizes L-cysteine residues "
                    "(CHEBI:29950) across juxtaposed polypeptide subunits to form an interchain "
                    "L-cystine (cross-link) (MOD:00034) that drives covalent protein complex "
                    "oligomerization (GO:0051259)."
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
                        node_id="GO:0051259",
                        label="protein complex oligomerization",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0051259",
                        description="Covalent quaternary subunit assembly via interchain disulfide bonds.",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="GO:0003756",
                        predicate="RO:0002233",
                        predicate_label="has input",
                        object="CHEBI:29950",
                        description="Oxidative disulfide formation consumes available cysteine thiols on partner subunits.",
                        reference="PMID:19005088",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "Our results indicate that individual cysteine residues that remain "
                            "available for disulfide bond formation in the folded monomer can form "
                            "interchain disulfide bonds with a variety of different cysteine "
                            "residues present in a companion subunit."
                        ),
                        notes="Inter-subunit cysteine oxidation (PMID:19005088).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0003756",
                        predicate="RO:0002234",
                        predicate_label="has output",
                        object="MOD:00034",
                        description="Oxidation forms an interchain L-cystine covalent bridge between companion subunits.",
                        reference="PMID:19005088",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "Our results indicate that individual cysteine residues that remain "
                            "available for disulfide bond formation in the folded monomer can form "
                            "interchain disulfide bonds with a variety of different cysteine "
                            "residues present in a companion subunit."
                        ),
                        notes="Interchain cystine crosslink formation (PMID:19005088).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0003756",
                        predicate="RO:0002411",
                        predicate_label="causally upstream of",
                        object="GO:0051259",
                        description="Interchain disulfide bond formation covalently links companion subunits into oligomers.",
                        reference="PMID:19005088",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "Our results indicate that individual cysteine residues that remain "
                            "available for disulfide bond formation in the folded monomer can form "
                            "interchain disulfide bonds with a variety of different cysteine "
                            "residues present in a companion subunit."
                        ),
                        notes="Covalent subunit cross-linking into oligomers (PMID:19005088).",
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
        evidence=(
            (
                "PMID:40763564",
                "Three conserved disulfide linkages form a cystine knot motif that confers high thermal and chemical stability.",
            ),
        ),
        detection_methods=(M_DSSP_SSBOND,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="cystine_knot_threaded_macrocycle_stability",
                label="Threaded three-disulfide cystine-knot topology locks tertiary fold and confers high stability",
                mechanism_summary=(
                    "Oxidative protein folding (GO:0006457) couples six conserved L-cysteine "
                    "residues (CHEBI:29950) into three interlocked L-cystine (cross-link) bridges "
                    "(MOD:00034) forming a cystine-knot motif, which is causally upstream of "
                    "regulation of protein stability (GO:0031647) against thermal and chemical degradation."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="CHEBI:29950",
                        label="L-cysteine residue",
                        node_type="RESIDUE",
                        grounding="CHEBI:29950",
                        description="Six conserved cysteine residues (CysI-CysVI) arranged in a cystine-knot sequence pattern.",
                    ),
                    CausalNodeSpec(
                        node_id="MOD:00034",
                        label="L-cystine (cross-link)",
                        node_type="PTM",
                        grounding="MOD:00034",
                        description="Three conserved disulfide linkages forming a cystine-knot network.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0006457",
                        label="protein folding",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0006457",
                        description="Oxidative folding assembling the three-disulfide cystine-knot topology.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0031647",
                        label="regulation of protein stability",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0031647",
                        description="Ultrastable tertiary structure resistant to thermal and chemical degradation.",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="GO:0006457",
                        predicate="RO:0002233",
                        predicate_label="has input",
                        object="CHEBI:29950",
                        description="Oxidative folding of cystine-knot peptides utilizes six conserved L-cysteine residues.",
                        reference="PMID:40763564",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Cyclotides are plant-derived cyclic peptides with three conserved "
                            "disulfide linkages, forming a cyclic cystine knot (CCK) motif. This "
                            "CCK topology makes them ultra stable structures and resistant to "
                            "thermal and chemical degradation."
                        ),
                        notes="Conserved cysteine residues forming three disulfide linkages (PMID:40763564).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0006457",
                        predicate="RO:0002234",
                        predicate_label="has output",
                        object="MOD:00034",
                        description="Oxidative folding produces three conserved L-cystine disulfide linkages in a cystine knot.",
                        reference="PMID:40763564",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Cyclotides are plant-derived cyclic peptides with three conserved "
                            "disulfide linkages, forming a cyclic cystine knot (CCK) motif. This "
                            "CCK topology makes them ultra stable structures and resistant to "
                            "thermal and chemical degradation."
                        ),
                        notes="Formation of three-disulfide cystine knot motif (PMID:40763564).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0006457",
                        predicate="RO:0002411",
                        predicate_label="causally upstream of",
                        object="GO:0031647",
                        description="The cystine-knot topology confers ultra-high resistance to thermal and chemical degradation.",
                        reference="PMID:40763564",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Cyclotides are plant-derived cyclic peptides with three conserved "
                            "disulfide linkages, forming a cyclic cystine knot (CCK) motif. This "
                            "CCK topology makes them ultra stable structures and resistant to "
                            "thermal and chemical degradation."
                        ),
                        notes="Ultrastability against thermal and chemical degradation (PMID:40763564).",
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
            (
                "PMID:42681370",
                "Thiol isomerases modify allosteric disulfide bonds in intracellular and extracellular proteins, thereby controlling protein function.",
            ),
        ),
        detection_methods=(M_DSSP_SSBOND,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="allosteric_disulfide_redox_switch_regulation",
                label="Reversible thiol-disulfide modification of allosteric cystine bonds controls protein activity",
                mechanism_summary=(
                    "Protein-disulfide reductase activity (GO:0015035) modifies an allosteric "
                    "L-cystine (cross-link) (MOD:00034) into reduced L-cysteine residues "
                    "(CHEBI:29950), driving conformational enzyme regulator activity (GO:0030234) "
                    "that regulates target catalytic activity (GO:0003824)."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="MOD:00034",
                        label="L-cystine (cross-link)",
                        node_type="PTM",
                        grounding="MOD:00034",
                        description="Allosteric disulfide bond in an intracellular or extracellular protein.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0015035",
                        label="protein-disulfide reductase activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0015035",
                        description="Thiol isomerase / oxidoreductase modifying allosteric disulfide bonds.",
                    ),
                    CausalNodeSpec(
                        node_id="CHEBI:29950",
                        label="L-cysteine residue",
                        node_type="RESIDUE",
                        grounding="CHEBI:29950",
                        description="Reduced dithiol cysteine pair generated upon allosteric disulfide cleavage.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0030234",
                        label="enzyme regulator activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0030234",
                        description="Redox-coupled allosteric switch controlling mature protein function.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0003824",
                        label="catalytic activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0003824",
                        description="Target protein function controlled by allosteric disulfide modification.",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="GO:0015035",
                        predicate="RO:0002233",
                        predicate_label="has input",
                        object="MOD:00034",
                        description="Thiol isomerases / oxidoreductases act on allosteric cystine disulfide bonds.",
                        reference="PMID:42681370",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Thiol isomerases are oxidoreductases that mediate disulfide bond "
                            "formation in nascent proteins of the endoplasmic reticulum to ensure "
                            "their structural integrity. In addition to its role in protein "
                            "folding, thiol isomerases can modify allosteric disulfide bonds in "
                            "both intracellular and extracellular proteins, thereby controlling "
                            "protein function."
                        ),
                        notes="Modification of allosteric disulfide bonds by thiol isomerases (PMID:42681370).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0015035",
                        predicate="RO:0002234",
                        predicate_label="has output",
                        object="CHEBI:29950",
                        description="Reductive cleavage converts the allosteric cystine crosslink into L-cysteine thiols.",
                        reference="PMID:42681370",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Thiol isomerases are oxidoreductases that mediate disulfide bond "
                            "formation in nascent proteins of the endoplasmic reticulum to ensure "
                            "their structural integrity. In addition to its role in protein "
                            "folding, thiol isomerases can modify allosteric disulfide bonds in "
                            "both intracellular and extracellular proteins, thereby controlling "
                            "protein function."
                        ),
                        notes="Reductive modification of allosteric disulfide bonds (PMID:42681370).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0015035",
                        predicate="RO:0002411",
                        predicate_label="causally upstream of",
                        object="GO:0030234",
                        description="Thiol isomerase modification of allosteric disulfides triggers an allosteric regulatory switch.",
                        reference="PMID:42681370",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Thiol isomerases are oxidoreductases that mediate disulfide bond "
                            "formation in nascent proteins of the endoplasmic reticulum to ensure "
                            "their structural integrity. In addition to its role in protein "
                            "folding, thiol isomerases can modify allosteric disulfide bonds in "
                            "both intracellular and extracellular proteins, thereby controlling "
                            "protein function."
                        ),
                        notes="Allosteric control of protein function via disulfide modification (PMID:42681370).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0030234",
                        predicate="RO:0002211",
                        predicate_label="regulates",
                        object="GO:0003824",
                        description="Allosteric disulfide switching controls target protein function.",
                        reference="PMID:42681370",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Thiol isomerases are oxidoreductases that mediate disulfide bond "
                            "formation in nascent proteins of the endoplasmic reticulum to ensure "
                            "their structural integrity. In addition to its role in protein "
                            "folding, thiol isomerases can modify allosteric disulfide bonds in "
                            "both intracellular and extracellular proteins, thereby controlling "
                            "protein function."
                        ),
                        notes="Regulation of protein function by allosteric disulfide switch (PMID:42681370).",
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
            "protocatechuate (3,4-dihydroxybenzoate) to 3-carboxy-cis,cis-muconate(3-) in the "
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
        evidence=(
            (
                "PMID:16101286",
                "The active site Fe(III) of protocatechuate 3,4-dioxygenase from Pseudomonas putida chelates protocatechuate (3,4-dihydroxybenzoate) for ring cleavage.",
            ),
            (
                "PMID:11029436",
                "PcaHG encodes protocatechuate 3,4-dioxygenase catalyzing the first step in protocatechuate catabolism to beta-carboxy-cis,cis-muconate.",
            ),
        ),
        detection_methods=(M_GO_COMPLEX,),
        definition_source="GO / CellStructureMech cross-Mech alignment",
        causal_graphs=(
            CausalGraphSpec(
                graph_id="pcagh_intradiol_ortho_cleavage",
                label="Non-heme Fe(III)-dependent intradiol ortho-cleavage of protocatechuate by the PcaGH complex",
                mechanism_summary=(
                    "The heterooligomeric protocatechuate 3,4-dioxygenase complex (GO:7770085) "
                    "incorporates a catalytic iron(3+) cofactor (CHEBI:29034) at the active site to "
                    "enable protocatechuate 3,4-dioxygenase activity (GO:0018578 / EC:1.13.11.3 / "
                    "RHEA:10084), converting 3,4-dihydroxybenzoate (CHEBI:36241) into "
                    "3-carboxy-cis,cis-muconate(3-) (CHEBI:57496) in protocatechuate catabolic "
                    "process, ortho-cleavage (GO:0019618)."
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
                        description="Catalytic non-heme high-spin Fe(III) ion coordinated by Tyr408, Tyr447, His460, His462, and OH-.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0018578",
                        label="protocatechuate 3,4-dioxygenase activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0018578",
                        description="Intradiol ring-cleaving dioxygenase catalysis (EC:1.13.11.3 / RHEA:10084).",
                    ),
                    CausalNodeSpec(
                        node_id="CHEBI:36241",
                        label="3,4-dihydroxybenzoate",
                        node_type="CHEMICAL",
                        grounding="CHEBI:36241",
                        description="Protocatechuate aromatic substrate chelating the active-site Fe(III).",
                    ),
                    CausalNodeSpec(
                        node_id="CHEBI:57496",
                        label="3-carboxy-cis,cis-muconate(3-)",
                        node_type="CHEMICAL",
                        grounding="CHEBI:57496",
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
                        predicate="RO:0002180",
                        predicate_label="has component",
                        object="CHEBI:29034",
                        description="The 3,4-PCD complex contains an active-site non-heme Fe(III) cofactor.",
                        reference="PMID:16101286",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "The active site Fe(III) of protocatechuate 3,4-dioxygenase (3,4-PCD) "
                            "from Pseudomonas putida is ligated axially by Tyr447 and His462 and "
                            "equatorially by Tyr408, His460, and OH(-). Tyr447 and OH(-) are "
                            "displaced as protocatechuate (3,4-dihydroxybenzoate, PCA) chelates "
                            "the iron and appear to serve as in situ bases to promote this process."
                        ),
                        notes="Active-site Fe(III) coordination in 3,4-PCD (PMID:16101286).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:7770085",
                        predicate="RO:0002327",
                        predicate_label="enables",
                        object="GO:0018578",
                        description="The PcaHG holoenzyme complex enables protocatechuate 3,4-dioxygenase catalysis.",
                        reference="PMID:11029436",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "The nucleotide sequence of the A348 pcaHGB genes, which encode "
                            "protocatechuate 3,4-dioxygenase (PcaHG) and "
                            "beta-carboxy-cis,cis-muconate cycloisomerase (PcaB) for the first "
                            "two steps in catabolism of the diphenolic protocatechuate, was "
                            "determined."
                        ),
                        notes="PcaHG complex encodes protocatechuate 3,4-dioxygenase activity (PMID:11029436).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0018578",
                        predicate="RO:0002233",
                        predicate_label="has input",
                        object="CHEBI:36241",
                        description="Protocatechuate 3,4-dioxygenase chelates 3,4-dihydroxybenzoate at the active-site Fe(III).",
                        reference="PMID:16101286",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "Tyr447 and OH(-) are displaced as protocatechuate "
                            "(3,4-dihydroxybenzoate, PCA) chelates the iron and appear to serve "
                            "as in situ bases to promote this process."
                        ),
                        notes="3,4-dihydroxybenzoate chelation at active-site Fe(III) (PMID:16101286).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0018578",
                        predicate="RO:0002234",
                        predicate_label="has output",
                        object="CHEBI:57496",
                        description="Protocatechuate 3,4-dioxygenase catalyzes ring cleavage to yield 3-carboxy-cis,cis-muconate(3-).",
                        reference="PMID:11029436",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "The nucleotide sequence of the A348 pcaHGB genes, which encode "
                            "protocatechuate 3,4-dioxygenase (PcaHG) and "
                            "beta-carboxy-cis,cis-muconate cycloisomerase (PcaB) for the first "
                            "two steps in catabolism of the diphenolic protocatechuate, was "
                            "determined."
                        ),
                        notes="Formation of beta-carboxy-cis,cis-muconate in first step of protocatechuate catabolism (PMID:11029436).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0018578",
                        predicate="RO:0002331",
                        predicate_label="involved in",
                        object="GO:0019618",
                        description="Protocatechuate 3,4-dioxygenase catalyzes the first step of protocatechuate ortho-cleavage catabolism.",
                        reference="PMID:11029436",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "The nucleotide sequence of the A348 pcaHGB genes, which encode "
                            "protocatechuate 3,4-dioxygenase (PcaHG) and "
                            "beta-carboxy-cis,cis-muconate cycloisomerase (PcaB) for the first "
                            "two steps in catabolism of the diphenolic protocatechuate, was "
                            "determined."
                        ),
                        notes="First step of protocatechuate ortho-cleavage catabolic pathway (PMID:11029436).",
                    ),
                ),
            ),
        ),
    ),
    # --- 13. SEQ_INITIATOR_METHIONINE (4 records) ---
    TraitSpec(
        rel_dir="sequence/initiator_methionine",
        filename="excised-initiator-methionine-site.yaml",
        identifier="proteintraitsmech:INIT_METHIONINE_EXCISED",
        label="methionyl-aminopeptidase-excised initiator methionine site",
        definition=(
            "An N-terminal initiator methionine position (Met1) that is co-translationally "
            "cleaved by methionyl-aminopeptidase (MetAP / MAP, EC 3.4.11.18) during nascent "
            "chain emergence from the ribosomal exit tunnel when the penultimate residue (P1', "
            "position 2) has a small side chain with a radius of gyration <= 1.29 A (Gly, Ala, "
            "Ser, Pro, Thr, Val, or Cys), exposing the penultimate residue as the mature "
            "N-terminus."
        ),
        trait_axis="SEQUENCE",
        trait_category="SEQ_INITIATOR_METHIONINE",
        parent_traits=("proteintraitsmech:UNIPROT_FT_SEQ_INITIATOR_METHIONINE",),
        synonyms=(
            ("cleaved N-terminal initiator methionine", "EXACT_SYNONYM"),
            ("MetAP-cleaved initiator Met1 site", "EXACT_SYNONYM"),
            ("N-terminal methionine excision (NME) positive site", "RELATED_SYNONYM"),
        ),
        xrefs=("GO:0004239", "GO:0006413"),
        sequence_pattern="^M[GASPTVC]",
        evidence=(
            (
                "PMID:2682640",
                "Extent of N-terminal methionine excision by methionyl-aminopeptidase is governed by the maximal side-chain length of the penultimate amino acid.",
            ),
        ),
        detection_methods=(M_MAP_NME_EXCISED,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="CG_INIT_METHIONINE_EXCISED",
                label="Co-translational initiator methionine excision by methionyl-aminopeptidase",
                mechanism_summary=(
                    "Translational initiation (GO:0006413) incorporates the N-terminal "
                    "L-methionine residue (CHEBI:16811) at position 1; when the penultimate "
                    "residue (Gly, Ala, Ser, Pro, Thr, Val, or Cys) at position 2 accommodates "
                    "within the S1' substrate pocket of methionyl-aminopeptidase (GO:0004239), "
                    "co-translational cleavage removes Met1 during protein processing (GO:0016485) "
                    "to expose the penultimate residue as the mature N-terminus."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="GO:0006413",
                        label="translational initiation",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0006413",
                        description="Translational initiation incorporating the N-terminal methionine residue at position 1 of the nascent polypeptide",
                    ),
                    CausalNodeSpec(
                        node_id="CHEBI:16811",
                        label="L-methionine",
                        node_type="RESIDUE",
                        grounding="CHEBI:16811",
                        description="N-terminal Met1 position adjacent to a small penultimate P1' residue (Gly, Ala, Ser, Pro, Thr, Val, or Cys) susceptible to co-translational excision",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0004239",
                        label="initiator methionyl aminopeptidase activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0004239",
                        description="Catalytic activity of methionyl-aminopeptidase (MAP, EC 3.4.11.18) cleaving the N-terminal initiator methionine from nascent polypeptides",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0016485",
                        label="protein processing",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0016485",
                        description="Co-translational proteolytic removal of the initiator methionine to expose the penultimate residue at the mature N-terminus",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="GO:0006413",
                        predicate="RO:0002213",
                        predicate_label="positively regulates",
                        object="CHEBI:16811",
                        description="Translational initiation incorporates the N-terminal methionine residue at position 1 of the nascent polypeptide.",
                        reference="PMID:2682640",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "In a significant fraction of the Escherichia coli cytosolic "
                            "proteins, the N-terminal methionine residue incorporated during the "
                            "translation initiation step is excised. The N-terminal methionine "
                            "excision is catalyzed by methionyl-aminopeptidase (MAP)."
                        ),
                        notes="Translation initiation incorporates N-terminal Met1 (PMID:2682640).",
                    ),
                    CausalEdgeSpec(
                        subject="CHEBI:16811",
                        predicate="RO:0000056",
                        predicate_label="participates in",
                        object="GO:0004239",
                        description="Small penultimate side-chain geometry at P1' allows N-terminal L-methionine to participate in productive substrate recognition and cleavage by methionyl-aminopeptidase.",
                        reference="PMID:2682640",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "From our results, methionine excision catalyzed by MAP is shown to "
                            "obey the following rule: the catalytic efficiency of MAP, and "
                            "therefore the extent of cleavage, decreases in parallel with the "
                            "increasing of the maximal side-chain length of the amino acid in "
                            "the penultimate position."
                        ),
                        notes="Penultimate side-chain length governs MAP cleavage efficiency (PMID:2682640).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0004239",
                        predicate="RO:0002213",
                        predicate_label="positively regulates",
                        object="GO:0016485",
                        description="Methionyl-aminopeptidase activity catalyzes N-terminal methionine excision during nascent polypeptide processing.",
                        reference="PMID:2682640",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "In a significant fraction of the Escherichia coli cytosolic "
                            "proteins, the N-terminal methionine residue incorporated during the "
                            "translation initiation step is excised. The N-terminal methionine "
                            "excision is catalyzed by methionyl-aminopeptidase (MAP)."
                        ),
                        notes="MAP catalyzes N-terminal methionine excision (PMID:2682640).",
                    ),
                ),
            ),
        ),
    ),
    TraitSpec(
        rel_dir="sequence/initiator_methionine",
        filename="retained-initiator-methionine-site.yaml",
        identifier="proteintraitsmech:INIT_METHIONINE_RETAINED",
        label="retained N-terminal initiator methionine site",
        definition=(
            "An N-terminal initiator methionine position (Met1) that is sterically protected "
            "from methionyl-aminopeptidase (MetAP / MAP) cleavage because the penultimate "
            "residue (P1', position 2) possesses a bulky, branched, or charged side chain "
            "(Arg, Asn, Asp, Gln, Glu, His, Ile, Leu, Lys, Met, Phe, Trp, or Tyr) that exceeds "
            "the steric exclusion radius of the MetAP S1' specificity pocket, retaining Met1 "
            "as the permanent N-terminal residue of the mature polypeptide."
        ),
        trait_axis="SEQUENCE",
        trait_category="SEQ_INITIATOR_METHIONINE",
        parent_traits=(),
        synonyms=(
            ("uncleaved initiator methionine site", "EXACT_SYNONYM"),
            ("MetAP-resistant N-terminal Met1 site", "EXACT_SYNONYM"),
            ("N-terminal methionine retention motif", "RELATED_SYNONYM"),
        ),
        xrefs=("GO:0004239", "GO:0006413"),
        sequence_pattern="^M[RNDQEHLKMFPWYI]",
        evidence=(
            (
                "PMID:2682640",
                "Increasing maximal side-chain length of the penultimate amino acid abolishes methionyl-aminopeptidase cleavage, resulting in N-terminal methionine retention.",
            ),
        ),
        detection_methods=(M_MAP_NME_RETAINED,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="CG_INIT_METHIONINE_RETAINED",
                label="Steric exclusion of bulky penultimate residues from methionyl-aminopeptidase retains N-terminal Met1",
                mechanism_summary=(
                    "When translational initiation (GO:0006413) incorporates N-terminal "
                    "L-methionine (CHEBI:16811) upstream of a penultimate residue with a long or "
                    "bulky side chain (Arg, Asn, Asp, Gln, Glu, His, Ile, Leu, Lys, Met, Phe, "
                    "Trp, or Tyr), steric hindrance in the S1' pocket negatively regulates "
                    "methionyl-aminopeptidase activity (GO:0004239), preventing proteolytic "
                    "N-terminal methionine excision during protein processing (GO:0016485) and "
                    "preserving Met1 on the mature protein."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="GO:0006413",
                        label="translational initiation",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0006413",
                        description="Incorporation of the N-terminal initiator methionine at position 1 of the nascent polypeptide",
                    ),
                    CausalNodeSpec(
                        node_id="CHEBI:16811",
                        label="L-methionine",
                        node_type="RESIDUE",
                        grounding="CHEBI:16811",
                        description="N-terminal Met1 position adjacent to a bulky or charged penultimate P1' residue whose side chain sterically blocks the methionyl-aminopeptidase S1' pocket",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0004239",
                        label="initiator methionyl aminopeptidase activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0004239",
                        description="Catalytic activity of methionyl-aminopeptidase (MAP, EC 3.4.11.18) toward nascent N-terminal methionine substrates",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0016485",
                        label="protein processing",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0016485",
                        description="N-terminal methionine excision pathway blocked by bulky penultimate side-chain steric exclusion, resulting in Met1 retention",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="GO:0006413",
                        predicate="RO:0002213",
                        predicate_label="positively regulates",
                        object="CHEBI:16811",
                        description="Translational initiation incorporates the N-terminal methionine residue at position 1 of the nascent polypeptide.",
                        reference="PMID:2682640",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "In a significant fraction of the Escherichia coli cytosolic "
                            "proteins, the N-terminal methionine residue incorporated during the "
                            "translation initiation step is excised. The N-terminal methionine "
                            "excision is catalyzed by methionyl-aminopeptidase (MAP)."
                        ),
                        notes="Translation initiation incorporates N-terminal Met1 (PMID:2682640).",
                    ),
                    CausalEdgeSpec(
                        subject="CHEBI:16811",
                        predicate="RO:0002212",
                        predicate_label="negatively regulates",
                        object="GO:0004239",
                        description="Bulky penultimate side chains decrease methionyl-aminopeptidase catalytic efficiency to zero, preventing Met1 excision.",
                        reference="PMID:2682640",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "From our results, methionine excision catalyzed by MAP is shown to "
                            "obey the following rule: the catalytic efficiency of MAP, and "
                            "therefore the extent of cleavage, decreases in parallel with the "
                            "increasing of the maximal side-chain length of the amino acid in "
                            "the penultimate position."
                        ),
                        notes="Large penultimate side chains inhibit MAP cleavage (PMID:2682640).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0004239",
                        predicate="RO:0002327",
                        predicate_label="enables",
                        object="GO:0016485",
                        description="Methionyl-aminopeptidase activity enables N-terminal methionine excision during protein processing, which is sterically blocked when the penultimate side chain is bulky.",
                        reference="PMID:2682640",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "From our results, methionine excision catalyzed by MAP is shown to "
                            "obey the following rule: the catalytic efficiency of MAP, and "
                            "therefore the extent of cleavage, decreases in parallel with the "
                            "increasing of the maximal side-chain length of the amino acid in "
                            "the penultimate position."
                        ),
                        notes="Suppressed MAP cleavage prevents N-terminal methionine excision (PMID:2682640).",
                    ),
                ),
            ),
        ),
    ),
    TraitSpec(
        rel_dir="sequence/initiator_methionine",
        filename="formylated-initiator-methionine-processing-site.yaml",
        identifier="proteintraitsmech:INIT_METHIONINE_FORMYLATED_NME",
        label="deformylase-dependent initiator formylmethionine processing site",
        definition=(
            "A prokaryotic, mitochondrial, or plastid N-terminal initiator methionine site "
            "translated as N-formyl-L-methionine (fMet, MOD:00030) that undergoes obligate "
            "sequential two-step N-terminal processing: (1) hydrolytic removal of the N-formyl "
            "group by peptide deformylase (PDF, EC 3.5.1.88) to unblock the alpha-amino group, "
            "which is strictly required before (2) methionyl-aminopeptidase (MAP, EC 3.4.11.18) "
            "can cleave the initiator methionine."
        ),
        trait_axis="SEQUENCE",
        trait_category="SEQ_INITIATOR_METHIONINE",
        parent_traits=("proteintraitsmech:UNIPROT_FT_SEQ_INITIATOR_METHIONINE",),
        synonyms=(
            ("PDF-MAP sequential N-terminal methionine excision site", "EXACT_SYNONYM"),
            ("prokaryotic N-formylmethionine deformylation-excision site", "EXACT_SYNONYM"),
            ("organellar fMet-NME processing site", "RELATED_SYNONYM"),
        ),
        xrefs=("MOD:00030", "GO:0008463", "GO:0004239"),
        sequence_pattern="^M[ACDEFGHIKLMNPQRSTVWY]",
        evidence=(
            (
                "PMID:18718933",
                "Removal of the N-formyl group from N-formylmethionine by peptide deformylase is essential to allow subsequent excision of the first methionine by methionyl-aminopeptidase.",
            ),
        ),
        detection_methods=(M_FMET_PDF,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="CG_INIT_METHIONINE_FORMYLATED_NME",
                label="Sequential peptide deformylase and methionyl-aminopeptidase N-terminal processing",
                mechanism_summary=(
                    "Nascent bacterial and organellar polypeptides initiate with "
                    "N-formyl-L-methionine (MOD:00030); peptide deformylase (GO:0008463) "
                    "hydrolyzes the N-formyl moiety, which unblocks and positively regulates "
                    "initiator methionyl aminopeptidase activity (GO:0004239) to execute "
                    "N-terminal protein processing (GO:0016485)."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="MOD:00030",
                        label="N-formyl-L-methionine residue",
                        node_type="PTM",
                        grounding="MOD:00030",
                        description="Nascent bacterial or organellar N-formyl-L-methionine (MOD:00030) initiator site requiring deformylation prior to methionyl-aminopeptidase cleavage",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0008463",
                        label="formylmethionine deformylase activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0008463",
                        description="Peptide deformylase (PDF, EC 3.5.1.88) activity hydrolyzing the N-terminal formyl group from nascent N-formylmethionine polypeptides",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0004239",
                        label="initiator methionyl aminopeptidase activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0004239",
                        description="Methionyl-aminopeptidase (MAP) activity excising the deformylated N-terminal methionine residue",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0016485",
                        label="protein processing",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0016485",
                        description="Sequential N-terminal deformylation and initiator methionine excision on nascent bacterial and organellar polypeptides",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="MOD:00030",
                        predicate="RO:0000056",
                        predicate_label="participates in",
                        object="GO:0008463",
                        description="Nascent N-formyl-L-methionine at position 1 participates as the substrate for peptide deformylase.",
                        reference="PMID:18718933",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "Because protein synthesis begins with N-formylmethionine in plant "
                            "endosymbiotic organelles, removal of the formyl group by peptide "
                            "deformylase (PDF) is essential to allowing the excision of the "
                            "first methionine."
                        ),
                        notes="Peptide deformylase removes the formyl group from nascent fMet (PMID:18718933).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0008463",
                        predicate="RO:0002213",
                        predicate_label="positively regulates",
                        object="GO:0004239",
                        description="Deformylation of N-formylmethionine by PDF is required before methionyl-aminopeptidase can cleave the first methionine.",
                        reference="PMID:18718933",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "Because protein synthesis begins with N-formylmethionine in plant "
                            "endosymbiotic organelles, removal of the formyl group by peptide "
                            "deformylase (PDF) is essential to allowing the excision of the "
                            "first methionine."
                        ),
                        notes="Deformylation by PDF is essential for subsequent Met1 excision (PMID:18718933).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0004239",
                        predicate="RO:0002331",
                        predicate_label="involved in",
                        object="GO:0016485",
                        description="Methionyl-aminopeptidase excision completes N-terminal protein processing of the deformylated nascent polypeptide.",
                        reference="PMID:18718933",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "Because protein synthesis begins with N-formylmethionine in plant "
                            "endosymbiotic organelles, removal of the formyl group by peptide "
                            "deformylase (PDF) is essential to allowing the excision of the "
                            "first methionine."
                        ),
                        notes="Sequential PDF and MAP action in N-terminal protein processing (PMID:18718933).",
                    ),
                ),
            ),
        ),
    ),
    TraitSpec(
        rel_dir="sequence/initiator_methionine",
        filename="n-acetylated-initiator-methionine-site.yaml",
        identifier="proteintraitsmech:INIT_METHIONINE_ACETYLATED",
        label="N-alpha-acetylated initiator methionine site",
        definition=(
            "A retained N-terminal initiator methionine position (Met1) that is co- or "
            "post-translationally acetylated on its alpha-amino group by N-terminal "
            "acetyltransferase complexes (primarily NatB on Met-Asp/Glu/Asn/Gln N-termini and "
            "NatC/NatE/NatF on Met-Leu/Ile/Phe/Trp/Tyr/Lys/Met N-termini) to form "
            "N-acetyl-L-methionine (MOD:00058), regulating protein folding, complex assembly, "
            "subcellular targeting, and Ac/N-degron-mediated turnover."
        ),
        trait_axis="SEQUENCE",
        trait_category="SEQ_INITIATOR_METHIONINE",
        parent_traits=("proteintraitsmech:INIT_METHIONINE_RETAINED",),
        synonyms=(
            ("NatB/NatC-acetylated initiator Met1 site", "EXACT_SYNONYM"),
            ("Nt-acetylated initiator methionine", "EXACT_SYNONYM"),
            ("Ac-Met1 N-terminal modification site", "RELATED_SYNONYM"),
        ),
        xrefs=("MOD:00058", "GO:0004596", "GO:0006474"),
        sequence_pattern="^M[DENQFLIWYKM]",
        evidence=(
            (
                "PMID:27498224",
                "N-terminal acetyltransferases (NATs) catalyze co- and post-translational N-terminal acetylation that modulates protein interactions, targeting, folding, and N-end rule turnover.",
            ),
        ),
        detection_methods=(M_NAT_PRED,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="CG_INIT_METHIONINE_ACETYLATED",
                label="N-alpha-acetylation of retained initiator methionine by N-terminal acetyltransferases",
                mechanism_summary=(
                    "Retained initiator methionine residues followed by acidic/polar (NatB) or "
                    "hydrophobic/amphipathic (NatC/NatE/NatF) penultimate residues are recognized "
                    "by protein-N-terminal amino-acid acetyltransferases (GO:0004596), driving "
                    "N-terminal protein amino acid acetylation (GO:0006474) to generate "
                    "N-acetyl-L-methionine (MOD:00058) and modulate protein folding (GO:0006457)."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="GO:0004596",
                        label="protein-N-terminal amino-acid acetyltransferase activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0004596",
                        description="Catalytic activity of N-terminal acetyltransferase complexes (NatB, NatC, NatE, NatF) transferring an acetyl group from acetyl-CoA to the alpha-amino group of retained Met1",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0006474",
                        label="N-terminal protein amino acid acetylation",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0006474",
                        description="Co- or post-translational acetylation of the N-terminal initiator methionine",
                    ),
                    CausalNodeSpec(
                        node_id="MOD:00058",
                        label="N-acetyl-L-methionine",
                        node_type="PTM",
                        grounding="MOD:00058",
                        description="N-terminal initiator methionine modified to N-acetyl-L-methionine (MOD:00058) by N-terminal acetyltransferases",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0006457",
                        label="protein folding",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0006457",
                        description="Protein folding, subcellular targeting, and interaction modulation governed by N-terminal acetylation",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="GO:0004596",
                        predicate="RO:0002213",
                        predicate_label="positively regulates",
                        object="GO:0006474",
                        description="N-terminal acetyltransferase (NatB/NatC/NatE/NatF) activity catalyzes co- and post-translational N-terminal protein amino acid acetylation of retained Met1.",
                        reference="PMID:27498224",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "N-terminal (Nt) acetylation is known to be a highly abundant "
                            "co-translational protein modification, but the recent discovery of "
                            "Golgi- and chloroplast-resident N-terminal acetyltransferases (NATs) "
                            "revealed that it can also be added post-translationally."
                        ),
                        notes="NATs catalyze co- and post-translational N-terminal acetylation (PMID:27498224).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0006474",
                        predicate="RO:0002234",
                        predicate_label="has output",
                        object="MOD:00058",
                        description="N-terminal acetylation of retained initiator methionine yields an N-acetyl-L-methionine (MOD:00058) residue at position 1.",
                        reference="PMID:27498224",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "N-terminal (Nt) acetylation is known to be a highly abundant "
                            "co-translational protein modification, but the recent discovery of "
                            "Golgi- and chloroplast-resident N-terminal acetyltransferases (NATs) "
                            "revealed that it can also be added post-translationally."
                        ),
                        notes="N-terminal acetylation generates N-acetyl-L-methionine at the N-terminus (PMID:27498224).",
                    ),
                    CausalEdgeSpec(
                        subject="MOD:00058",
                        predicate="RO:0002331",
                        predicate_label="involved in",
                        object="GO:0006457",
                        description="The N-acetyl-L-methionine modification at the N-terminus modulates protein folding, subcellular targeting, and protein-protein interactions.",
                        reference="PMID:27498224",
                        evidence_code="ECO:0000305",
                        snippet="Nt-acetylation also modulates protein interactions, targeting, and folding.",
                        notes="Nt-acetylation modulates protein folding and interactions (PMID:27498224).",
                    ),
                ),
            ),
        ),
    ),
    # --- 14. SEQ_MATURE_CHAIN (4 records) ---
    TraitSpec(
        rel_dir="sequence/mature_chain",
        filename="signal-peptidase-processed-mature-chain.yaml",
        identifier="proteintraitsmech:MATURE_CHAIN_SECRETED",
        label="signal-peptidase-processed mature polypeptide chain",
        definition=(
            "A mature functional polypeptide chain (SO:0000419) generated by endoproteolytic "
            "cleavage of an N-terminal secretory signal peptide or bacterial lipoprotein leader "
            "peptide by type I/II/III signal peptidase during or immediately following translocation "
            "across the endoplasmic reticulum, bacterial cytoplasmic, or archaeal plasma membrane."
        ),
        trait_axis="SEQUENCE",
        trait_category="SEQ_MATURE_CHAIN",
        parent_traits=("proteintraitsmech:UNIPROT_FT_SEQ_MATURE_CHAIN",),
        synonyms=(
            ("secreted mature protein chain", "EXACT_SYNONYM"),
            ("post-signal-peptide mature polypeptide region", "EXACT_SYNONYM"),
        ),
        xrefs=("SO:0000419", "GO:0016485", "GO:0051604"),
        evidence=(
            (
                "PMID:34980915",
                "Signal peptides control protein secretion and translocation in all living organisms and are cleaved off during translocation to release the mature polypeptide chain.",
            ),
        ),
        detection_methods=(M_SIGNALP6,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="CG_MATURE_CHAIN_SECRETED",
                label="Signal peptidase cleavage of N-terminal signal peptide yields mature secreted chain",
                mechanism_summary=(
                    "An N-terminal signal peptide (SO:0000418) directs membrane translocation "
                    "and proteolytic protein processing (GO:0016485) by signal peptidase, "
                    "releasing the signal-peptidase-processed mature polypeptide chain (SO:0000419) "
                    "for protein secretion (GO:0009306)."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="SO:0000418",
                        label="signal_peptide",
                        node_type="MOTIF",
                        grounding="SO:0000418",
                        description="Cleavable N-terminal secretory signal peptide directing translocation and subsequent cleavage by signal peptidase",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0016485",
                        label="protein processing",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0016485",
                        description="Proteolytic removal of the N-terminal signal peptide during or immediately following membrane translocation",
                    ),
                    CausalNodeSpec(
                        node_id="SO:0000419",
                        label="mature_protein_region",
                        node_type="DOMAIN",
                        grounding="SO:0000419",
                        description="Mature functional polypeptide region (SO:0000419) released after signal peptide cleavage",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0009306",
                        label="protein secretion",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0009306",
                        description="Translocation and release of the mature processed polypeptide across the secretory membrane",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="SO:0000418",
                        predicate="RO:0002213",
                        predicate_label="positively regulates",
                        object="GO:0016485",
                        description="The N-terminal signal peptide directs co- or post-translational translocation and proteolytic cleavage by signal peptidase.",
                        reference="PMID:34980915",
                        evidence_code="ECO:0000269",
                        snippet="Signal peptides (SPs) are short amino acid sequences that control protein secretion and translocation in all living organisms.",
                        notes="Signal peptides control secretion and translocation processing (PMID:34980915).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0016485",
                        predicate="RO:0002234",
                        predicate_label="has output",
                        object="SO:0000419",
                        description="Proteolytic removal of the signal peptide after membrane translocation releases the mature polypeptide chain.",
                        reference="PMID:34980915",
                        evidence_code="ECO:0000269",
                        snippet="SPs can be cleaved off after the protein has been translocated across the membrane.",
                        notes="Release of the mature polypeptide chain upon signal peptide cleavage (PMID:34980915).",
                    ),
                    CausalEdgeSpec(
                        subject="SO:0000419",
                        predicate="RO:0002331",
                        predicate_label="involved in",
                        object="GO:0009306",
                        description="The signal-peptidase-processed mature polypeptide chain is secreted across the membrane into its target compartment.",
                        reference="PMID:34980915",
                        evidence_code="ECO:0000269",
                        snippet="Signal peptides (SPs) are short amino acid sequences that control protein secretion and translocation in all living organisms.",
                        notes="Mature polypeptide translocation and secretion across the membrane (PMID:34980915).",
                    ),
                ),
            ),
        ),
    ),
    TraitSpec(
        rel_dir="sequence/mature_chain",
        filename="proprotein-convertase-processed-mature-chain.yaml",
        identifier="proteintraitsmech:MATURE_CHAIN_PROPROTEIN_CLEAVED",
        label="proprotein-convertase-processed mature polypeptide chain",
        definition=(
            "A mature bioactive polypeptide or peptide hormone/neuropeptide chain (SO:0000419) "
            "excised from a larger proprotein, prohormone, or polyprotein precursor by "
            "site-specific endopeptidases (such as subtilisin/kexin-like proprotein convertases "
            "or secretory-vesicle cathepsin L) at monobasic or dibasic cleavage motifs within "
            "the secretory pathway."
        ),
        trait_axis="SEQUENCE",
        trait_category="SEQ_MATURE_CHAIN",
        parent_traits=("proteintraitsmech:UNIPROT_FT_SEQ_MATURE_CHAIN",),
        synonyms=(
            ("prohormone-derived mature peptide chain", "EXACT_SYNONYM"),
            ("polyprotein-processed mature polypeptide chain", "RELATED_SYNONYM"),
            ("convertase-cleaved mature chain", "EXACT_SYNONYM"),
        ),
        xrefs=("SO:0000419", "GO:0016486", "GO:0004175"),
        evidence=(
            (
                "PMID:18184105",
                "Neuropeptides and peptide hormones are synthesized from proneuropeptide or prohormone precursors that undergo proteolytic processing in secretory vesicles to yield mature active peptides.",
            ),
        ),
        detection_methods=(M_PROPEP,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="CG_MATURE_CHAIN_PROPROTEIN_CLEAVED",
                label="Endoproteolytic cleavage of prohormone/proprotein precursors yields mature active chains",
                mechanism_summary=(
                    "Subtilisin-like proprotein convertases and secretory-vesicle cysteine "
                    "endopeptidases (GO:0004175) catalyze peptide hormone processing "
                    "(GO:0016486) of proprotein precursors to produce the mature polypeptide "
                    "chain (SO:0000419), which enables downstream hormone or signaling activity "
                    "(GO:0005179)."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="GO:0004175",
                        label="endopeptidase activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0004175",
                        description="Proprotein convertase / processing endopeptidase activity cleaving dibasic or monobasic sites in prohormone and proneuropeptide precursors",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0016486",
                        label="peptide hormone processing",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0016486",
                        description="Proteolytic processing of prohormone and proneuropeptide precursors within secretory vesicles",
                    ),
                    CausalNodeSpec(
                        node_id="SO:0000419",
                        label="mature_protein_region",
                        node_type="DOMAIN",
                        grounding="SO:0000419",
                        description="Bioactive mature polypeptide or peptide chain (SO:0000419) excised from a multivalent precursor",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0005179",
                        label="hormone activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0005179",
                        description="Receptor-mediated signaling or endocrine activity of the mature processed peptide",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="GO:0004175",
                        predicate="RO:0002213",
                        predicate_label="positively regulates",
                        object="GO:0016486",
                        description="Proprotein convertases and processing endopeptidases catalyze proteolytic processing of prohormone precursors.",
                        reference="PMID:18184105",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Neuropeptides are synthesized from protein precursors (termed "
                            "proneuropeptides or prohormones) that require proteolytic "
                            "processing primarily within secretory vesicles that store and "
                            "secrete the mature neuropeptides to control target cellular and "
                            "organ systems."
                        ),
                        notes="Proteolytic processing of proneuropeptides and prohormones in secretory vesicles (PMID:18184105).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0016486",
                        predicate="RO:0002234",
                        predicate_label="has output",
                        object="SO:0000419",
                        description="Proteolytic prohormone processing yields the mature bioactive peptide or polypeptide chain.",
                        reference="PMID:18184105",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Neuropeptides are synthesized from protein precursors (termed "
                            "proneuropeptides or prohormones) that require proteolytic "
                            "processing primarily within secretory vesicles that store and "
                            "secrete the mature neuropeptides to control target cellular and "
                            "organ systems."
                        ),
                        notes="Generation of mature peptide chains from prohormone precursors (PMID:18184105).",
                    ),
                    CausalEdgeSpec(
                        subject="SO:0000419",
                        predicate="RO:0002327",
                        predicate_label="enables",
                        object="GO:0005179",
                        description="The excised mature peptide chain mediates intercellular hormone and neurotransmitter signaling.",
                        reference="PMID:18184105",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Peptide neurotransmitters and peptide hormones, collectively known "
                            "as neuropeptides, are required for cell-cell communication in "
                            "neurotransmission and for regulation of endocrine functions."
                        ),
                        notes="Mature peptide hormones regulate neurotransmission and endocrine functions (PMID:18184105).",
                    ),
                ),
            ),
        ),
    ),
    TraitSpec(
        rel_dir="sequence/mature_chain",
        filename="intein-spliced-mature-extein-chain.yaml",
        identifier="proteintraitsmech:MATURE_CHAIN_INTEIN_SPLICED",
        label="intein-spliced mature extein polypeptide chain",
        definition=(
            "A contiguous mature host polypeptide chain (SO:0000419) formed post-translationally "
            "by autocatalytic protein splicing (GO:0016539), in which an internal intervening "
            "polypeptide (intein) catalyzes its own excision from flanking N-extein and "
            "C-extein segments coupled to native peptide-bond ligation of the exteins."
        ),
        trait_axis="SEQUENCE",
        trait_category="SEQ_MATURE_CHAIN",
        parent_traits=("proteintraitsmech:UNIPROT_FT_SEQ_MATURE_CHAIN",),
        synonyms=(
            ("ligated N/C-extein mature chain", "EXACT_SYNONYM"),
            ("protein-splicing mature host polypeptide", "EXACT_SYNONYM"),
            ("extein-ligated mature protein region", "RELATED_SYNONYM"),
        ),
        xrefs=("SO:0000419", "GO:0016539", "GO:0051604"),
        evidence=(
            (
                "PMID:24695729",
                "Inteins catalyze their excision from flanking polypeptides (exteins) concomitant with extein ligation to produce a mature host protein via sequential nucleophilic displacement reactions.",
            ),
        ),
        detection_methods=(M_INTEIN,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="CG_MATURE_CHAIN_INTEIN_SPLICED",
                label="Autocatalytic intein excision and extein ligation produce mature host chain",
                mechanism_summary=(
                    "Autocatalytic nucleophilic displacement activity (GO:0003824) of the internal "
                    "intein element drives intein-mediated protein splicing (GO:0016539), excising "
                    "the intervening intein and ligating the flanking N- and C-exteins into a "
                    "contiguous mature extein polypeptide chain (SO:0000419) to complete "
                    "protein maturation (GO:0051604)."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="GO:0003824",
                        label="catalytic activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0003824",
                        description="Autocatalytic nucleophilic acyl-shift, transesterification, and asparagine cyclization activity of the intein splicing domain",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0016539",
                        label="intein-mediated protein splicing",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0016539",
                        description="Autocatalytic excision of an internal protein splicing element (intein) coupled to peptide-bond ligation of flanking N- and C-exteins",
                    ),
                    CausalNodeSpec(
                        node_id="SO:0000419",
                        label="mature_protein_region",
                        node_type="DOMAIN",
                        grounding="SO:0000419",
                        description="Contiguous mature host polypeptide chain (SO:0000419) formed by native peptide bond ligation of N-extein and C-extein",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0051604",
                        label="protein maturation",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0051604",
                        description="Maturation of the functional host protein following intein excision and extein ligation",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="GO:0003824",
                        predicate="RO:0002213",
                        predicate_label="positively regulates",
                        object="GO:0016539",
                        description="Sequential autocatalytic nucleophilic displacement reactions by the intein catalytic residues drive protein splicing.",
                        reference="PMID:24695729",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Splicing requires sequential nucleophilic displacement reactions "
                            "catalyzed by strategies similar to proteases and asparagine lyases."
                        ),
                        notes="Sequential nucleophilic displacement reactions catalyze protein splicing (PMID:24695729).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0016539",
                        predicate="RO:0002234",
                        predicate_label="has output",
                        object="SO:0000419",
                        description="Intein excision concomitant with N- and C-extein ligation produces the contiguous mature host polypeptide chain.",
                        reference="PMID:24695729",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Inteins are nature's escape artists; they facilitate their "
                            "excision from flanking polypeptides (exteins) concomitant with "
                            "extein ligation to produce a mature host protein."
                        ),
                        notes="Intein excision and extein ligation yield the mature host protein (PMID:24695729).",
                    ),
                    CausalEdgeSpec(
                        subject="SO:0000419",
                        predicate="RO:0002331",
                        predicate_label="involved in",
                        object="GO:0051604",
                        description="Formation of the spliced extein chain restores the mature functional host protein.",
                        reference="PMID:24695729",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Inteins are nature's escape artists; they facilitate their "
                            "excision from flanking polypeptides (exteins) concomitant with "
                            "extein ligation to produce a mature host protein."
                        ),
                        notes="Extein ligation completes maturation of the host protein (PMID:24695729).",
                    ),
                ),
            ),
        ),
    ),
    TraitSpec(
        rel_dir="sequence/mature_chain",
        filename="proteolytically-excised-bioactive-peptide-chain.yaml",
        identifier="proteintraitsmech:MATURE_CHAIN_BIOACTIVE_PEPTIDE",
        label="proteolytically excised bioactive antimicrobial/effector peptide chain",
        definition=(
            "A short mature bioactive C-terminal or internal peptide chain (SO:0000419) "
            "liberated from an inactive holoprotein precursor (such as a cathelicidin, "
            "defensin, or ribosomally synthesized bacteriocin proprotein) by granule or "
            "extracellular endoproteases (including proteinase 3, neutrophil elastase, or "
            "leader peptidases) to unmask membrane-active antimicrobial or host-defense "
            "activity."
        ),
        trait_axis="SEQUENCE",
        trait_category="SEQ_MATURE_CHAIN",
        parent_traits=("proteintraitsmech:UNIPROT_FT_SEQ_MATURE_CHAIN",),
        synonyms=(
            ("holoprotein-cleaved mature antimicrobial peptide chain", "EXACT_SYNONYM"),
            ("mature host-defense peptide region", "RELATED_SYNONYM"),
        ),
        xrefs=("SO:0000419", "GO:0002777", "GO:0042742"),
        evidence=(
            (
                "PMID:11134217",
                "Cathelicidins are synthesized as inactive holoproteins whose C-terminal antimicrobial peptide chain must be proteolytically cleaved by elastase or proteinase 3 to become active.",
            ),
        ),
        detection_methods=(M_PROPEP,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="CG_MATURE_CHAIN_BIOACTIVE_PEPTIDE",
                label="Proteolytic liberation of C-terminal bioactive antimicrobial peptide chain from holoprotein precursor",
                mechanism_summary=(
                    "Granule or extracellular endopeptidase activity (GO:0004175, such as "
                    "neutrophil elastase or proteinase 3) drives antimicrobial peptide "
                    "biosynthesis (GO:0002777) by cleaving the N-terminal pro-domain from "
                    "the inactive holoprotein to release the mature bioactive peptide chain "
                    "(SO:0000419), which mediates antimicrobial humoral defense (GO:0061844)."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="GO:0004175",
                        label="endopeptidase activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0004175",
                        description="Serine endoprotease activity (such as neutrophil elastase or proteinase 3) cleaving the inactive holoprotein precursor",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0002777",
                        label="antimicrobial peptide biosynthetic process",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0002777",
                        description="Proteolytic cleavage of an inactive holoprotein precursor (such as a cathelicidin or bacteriocin proprotein) to release the active C-terminal peptide",
                    ),
                    CausalNodeSpec(
                        node_id="SO:0000419",
                        label="mature_protein_region",
                        node_type="DOMAIN",
                        grounding="SO:0000419",
                        description="Mature bioactive antimicrobial or effector peptide chain (SO:0000419) liberated from its proprotein precursor",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0061844",
                        label="antimicrobial humoral immune response mediated by antimicrobial peptide",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0061844",
                        description="Direct antimicrobial defense mediated by the mature excised peptide",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="GO:0004175",
                        predicate="RO:0002213",
                        predicate_label="positively regulates",
                        object="GO:0002777",
                        description="Granule serine endoproteases such as neutrophil elastase or proteinase 3 cleave inactive cathelicidin holoproteins to initiate active antimicrobial peptide generation.",
                        reference="PMID:11134217",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "Bovine and porcine cathelicidins are cleaved by elastase from the "
                            "azurophil granules to yield the active antimicrobial peptides."
                        ),
                        notes="Elastase endopeptidase activity cleaves cathelicidin holoproteins (PMID:11134217).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0002777",
                        predicate="RO:0002234",
                        predicate_label="has output",
                        object="SO:0000419",
                        description="Proteolytic processing of the holoprotein precursor liberates the active C-terminal antimicrobial peptide chain.",
                        reference="PMID:11134217",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "Bovine and porcine cathelicidins are cleaved by elastase from the "
                            "azurophil granules to yield the active antimicrobial peptides."
                        ),
                        notes="Proteolytic cleavage of cathelicidin holoprotein yields active antimicrobial peptide (PMID:11134217).",
                    ),
                    CausalEdgeSpec(
                        subject="SO:0000419",
                        predicate="RO:0002331",
                        predicate_label="involved in",
                        object="GO:0061844",
                        description="Once cleaved from the holoprotein precursor, the mature C-terminal peptide chain executes antimicrobial defense.",
                        reference="PMID:11134217",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "Cathelicidins are a family of antimicrobial proteins found in the "
                            "peroxidase-negative granules of neutrophils. The known biologic "
                            "functions reside in the C-terminus, which must be cleaved from the "
                            "holoprotein to become active."
                        ),
                        notes="Biological antimicrobial activity resides in the cleaved C-terminal peptide chain (PMID:11134217).",
                    ),
                ),
            ),
        ),
    ),
    # --- 15. SEQ_TRANSIT_PEPTIDE additions (3 records) ---
    TraitSpec(
        rel_dir="sequence/transit_peptide",
        filename="mitochondrial-intermembrane-space-bipartite-transit-peptide.yaml",
        identifier="proteintraitsmech:TRANSIT_PEPTIDE_MITO_IMS",
        label="mitochondrial intermembrane-space bipartite transit peptide",
        definition=(
            "A cleavable bipartite N-terminal mitochondrial transit peptide composed of an "
            "N-terminal positively charged matrix-targeting presequence (cleaved in the matrix "
            "by mitochondrial processing peptidase, MPP) followed immediately by a hydrophobic "
            "stop-transfer sorting signal that arrests translocation in the TIM23 channel and "
            "is cleaved on the intermembrane-space side of the inner membrane by the inner "
            "membrane peptidase complex (Imp1p/Imp2p, IMP) to release the soluble protein into "
            "the mitochondrial intermembrane space (GO:0005758)."
        ),
        trait_axis="SEQUENCE",
        trait_category="SEQ_TRANSIT_PEPTIDE",
        parent_traits=(
            "proteintraitsmech:UNIPROT_FT_SEQ_TRANSIT_PEPTIDE",
            "proteintraitsmech:TRANSIT_PEPTIDE_MITOCHONDRIAL",
        ),
        synonyms=(
            ("mitochondrial IMS stop-transfer bipartite presequence", "EXACT_SYNONYM"),
            ("Imp1/Imp2-cleaved intermembrane space sorting signal", "EXACT_SYNONYM"),
        ),
        xrefs=("SO:0001808", "GO:0004175", "GO:0045041", "GO:0005758"),
        evidence=(
            (
                "PMID:8266095",
                "The mitochondrial inner membrane protease (Imp1p/Imp2p) catalyzes cleavage of intermembrane space sorting signals for maturation of proteins delivered to the mitochondrial intermembrane space.",
            ),
        ),
        detection_methods=(M_TARGETP2_V2,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="CG_TRANSIT_PEPTIDE_MITO_IMS",
                label="Bipartite MTS + stop-transfer sorting and IMP cleavage into the mitochondrial intermembrane space",
                mechanism_summary=(
                    "A mitochondrial intermembrane-space bipartite transit peptide (SO:0001808) "
                    "arrests TIM23 translocation and presents its hydrophobic sorting signal to "
                    "the inner membrane protease complex (Imp1p/Imp2p) endopeptidase activity "
                    "(GO:0004175), which positively regulates protein import into the "
                    "mitochondrial intermembrane space (GO:0045041) to deliver the mature "
                    "protein into the mitochondrial intermembrane space (GO:0005758)."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="SO:0001808",
                        label="mitochondrial_targeting_signal",
                        node_type="MOTIF",
                        grounding="SO:0001808",
                        description="Bipartite mitochondrial presequence containing an N-terminal matrix-targeting signal followed by a hydrophobic stop-transfer intermembrane-space sorting signal cleaved by Imp1p/Imp2p",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0004175",
                        label="endopeptidase activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0004175",
                        description="Inner membrane protease (Imp1p/Imp2p) endopeptidase activity cleaving intermembrane-space sorting signals at the inner-membrane IMS face",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0045041",
                        label="protein import into mitochondrial intermembrane space",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0045041",
                        description="Stop-transfer sorting and inner-membrane protease maturation of proteins imported into the mitochondrial intermembrane space",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0005758",
                        label="mitochondrial intermembrane space",
                        node_type="CELLULAR_LOCALIZATION",
                        grounding="GO:0005758",
                        description="Mitochondrial intermembrane space compartment between the outer and inner mitochondrial membranes",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="SO:0001808",
                        predicate="RO:0000056",
                        predicate_label="participates in",
                        object="GO:0004175",
                        description="The intermembrane-space sorting signal of the bipartite presequence participates as the cleavage substrate for the inner membrane protease (Imp1p/Imp2p).",
                        reference="PMID:8266095",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "In addition to its catalyzing the cleavage of intermembrane space "
                            "sorting signals, Imp2p is required for the stable and functional "
                            "expression of Imp1p."
                        ),
                        notes="Imp1p/Imp2p cleaves intermembrane space sorting signals (PMID:8266095).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0004175",
                        predicate="RO:0002213",
                        predicate_label="positively regulates",
                        object="GO:0045041",
                        description="Inner membrane protease endopeptidase cleavage drives maturation of proteins imported into the mitochondrial intermembrane space.",
                        reference="PMID:8266095",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "The mitochondrial inner membrane protease is required for the "
                            "maturation of mitochondrial proteins that are delivered to the "
                            "intermembrane space."
                        ),
                        notes="IMP endopeptidase activity is required for IMS protein import and maturation (PMID:8266095).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0045041",
                        predicate="RO:0002339",
                        predicate_label="has target end location",
                        object="GO:0005758",
                        description="Inner membrane protease maturation delivers the processed soluble protein to the mitochondrial intermembrane space.",
                        reference="PMID:8266095",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "The mitochondrial inner membrane protease is required for the "
                            "maturation of mitochondrial proteins that are delivered to the "
                            "intermembrane space."
                        ),
                        notes="Maturation of proteins delivered to the mitochondrial intermembrane space (PMID:8266095).",
                    ),
                ),
            ),
        ),
    ),
    TraitSpec(
        rel_dir="sequence/transit_peptide",
        filename="apicoplast-bipartite-transit-peptide.yaml",
        identifier="proteintraitsmech:TRANSIT_PEPTIDE_APICOPLAST",
        label="apicoplast bipartite transit peptide",
        definition=(
            "A cleavable bipartite N-terminal leader sequence in apicomplexan parasites "
            "(such as Plasmodium and Toxoplasma) consisting of an N-terminal hydrophobic "
            "secretory signal peptide that mediates co-translational entry into the endoplasmic "
            "reticulum followed by a net-positively charged plant-like plastid transit peptide "
            "that directs subsequent transport across the four surrounding membranes into the "
            "apicoplast stroma (GO:0020011), with both segments removed stepwise during import."
        ),
        trait_axis="SEQUENCE",
        trait_category="SEQ_TRANSIT_PEPTIDE",
        parent_traits=("proteintraitsmech:UNIPROT_FT_SEQ_TRANSIT_PEPTIDE",),
        synonyms=(
            ("apicoplast bipartite presequence", "EXACT_SYNONYM"),
            ("SP+TP apicoplast targeting leader", "EXACT_SYNONYM"),
            ("secondary plastid bipartite transit peptide", "BROAD_SYNONYM"),
        ),
        xrefs=("SO:0000725", "GO:0033365", "GO:0016485", "GO:0020011"),
        evidence=(
            (
                "PMID:10775264",
                "Protein targeting to the four-membrane-bound apicoplast of Plasmodium falciparum is a two-step process mediated by bipartite N-terminal pre-sequences consisting of a signal peptide and a plant-like transit peptide removed stepwise.",
            ),
        ),
        detection_methods=(M_TARGETP2_V2,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="CG_TRANSIT_PEPTIDE_APICOPLAST",
                label="Two-step secretory-to-apicoplast import via bipartite signal + transit presequence",
                mechanism_summary=(
                    "An apicoplast bipartite transit peptide (SO:0000725) combines an ER "
                    "signal peptide with a plant-like transit peptide to drive two-step "
                    "organellar protein localization (GO:0033365), followed by stepwise "
                    "proteolytic protein processing (GO:0016485) that delivers the mature "
                    "polypeptide into the apicoplast lumen (GO:0020011)."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="SO:0000725",
                        label="transit_peptide",
                        node_type="MOTIF",
                        grounding="SO:0000725",
                        description="Bipartite N-terminal presequence composed of a secretory signal peptide followed by a plant-like plastid transit peptide removed stepwise during apicoplast import",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0033365",
                        label="protein localization to organelle",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0033365",
                        description="Two-step secretory-to-plastid translocation targeting nuclear-encoded proteins across the four apicoplast membranes",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0016485",
                        label="protein processing",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0016485",
                        description="Stepwise proteolytic removal of the N-terminal signal peptide in the ER and the plastid transit peptide in the apicoplast",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0020011",
                        label="apicoplast",
                        node_type="CELLULAR_LOCALIZATION",
                        grounding="GO:0020011",
                        description="Four-membrane-bound non-photosynthetic relict plastid of apicomplexan parasites",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="SO:0000725",
                        predicate="RO:0002331",
                        predicate_label="involved in",
                        object="GO:0033365",
                        description="The bipartite signal peptide + transit peptide presequence mediates two-step import into the apicoplast.",
                        reference="PMID:10775264",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "We demonstrate that protein targeting is at least a two-step "
                            "process mediated by bipartite N-terminal pre-sequences that consist "
                            "of a signal peptide for entry into the secretory pathway and a "
                            "plant-like transit peptide for subsequent import into the apicoplast."
                        ),
                        notes="Bipartite signal + transit presequence mediates two-step apicoplast targeting (PMID:10775264).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0033365",
                        predicate="RO:0002411",
                        predicate_label="causally upstream of",
                        object="GO:0016485",
                        description="Two-step organellar targeting is accompanied by stepwise proteolytic removal of the signal-peptide and transit-peptide components.",
                        reference="PMID:10775264",
                        evidence_code="ECO:0000269",
                        snippet="The pre-sequence components are removed stepwise during apicoplast targeting.",
                        notes="Stepwise presequence cleavage during apicoplast import (PMID:10775264).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0016485",
                        predicate="RO:0002339",
                        predicate_label="has target end location",
                        object="GO:0020011",
                        description="Stepwise processing of the bipartite presequence delivers the mature protein into the apicoplast lumen.",
                        reference="PMID:10775264",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "We demonstrate that protein targeting is at least a two-step "
                            "process mediated by bipartite N-terminal pre-sequences that consist "
                            "of a signal peptide for entry into the secretory pathway and a "
                            "plant-like transit peptide for subsequent import into the apicoplast."
                        ),
                        notes="Processed protein is delivered to the apicoplast lumen (PMID:10775264).",
                    ),
                ),
            ),
        ),
    ),
    TraitSpec(
        rel_dir="sequence/transit_peptide",
        filename="hydrogenosomal-mitosomal-transit-presequence.yaml",
        identifier="proteintraitsmech:TRANSIT_PEPTIDE_HYDROGENOSOME_MITOSOME",
        label="hydrogenosomal / mitosomal N-terminal transit presequence",
        definition=(
            "A short cleavable N-terminal transit presequence (typically 5-25 residues, "
            "enriched in sub-terminal arginine/lysine residues proximal to the cleavage site) "
            "on nuclear-encoded proteins of anaerobic protists that directs import across the "
            "double membrane of mitochondrion-related organelles — hydrogenosomes (GO:0042566) "
            "and mitosomes (GO:0032047) — and is proteolytically removed in the organellar "
            "lumen by hydrogenosomal or mitosomal processing peptidase (HPP / GPP)."
        ),
        trait_axis="SEQUENCE",
        trait_category="SEQ_TRANSIT_PEPTIDE",
        parent_traits=("proteintraitsmech:UNIPROT_FT_SEQ_TRANSIT_PEPTIDE",),
        synonyms=(
            ("hydrogenosomal targeting presequence", "EXACT_SYNONYM"),
            ("mitosomal N-terminal targeting presequence", "EXACT_SYNONYM"),
            ("MRO matrix transit peptide", "RELATED_SYNONYM"),
        ),
        xrefs=("SO:0000725", "GO:0042566", "GO:0032047", "GO:0033365"),
        evidence=(
            (
                "PMID:16040811",
                "Proteins targeted into Giardia mitosomes and Trichomonas hydrogenosomes carry conserved N-terminal targeting presequences recognized by a shared TIM/processing-peptidase import machinery.",
            ),
        ),
        detection_methods=(M_TARGETP2_V2,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="CG_TRANSIT_PEPTIDE_HYDROGENOSOME_MITOSOME",
                label="N-terminal presequence-directed import and processing in hydrogenosomes and mitosomes",
                mechanism_summary=(
                    "A short N-terminal transit presequence (SO:0000725) is recognized by the "
                    "conserved mitochondrion-related organelle import and processing-peptidase "
                    "machinery (GO:0033365), targeting proteins into mitosomes (GO:0032047) "
                    "and hydrogenosomes (GO:0042566)."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="SO:0000725",
                        label="transit_peptide",
                        node_type="MOTIF",
                        grounding="SO:0000725",
                        description="Short N-terminal targeting presequence recognized by hydrogenosomal and mitosomal protein import and processing peptidase machinery",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0033365",
                        label="protein localization to organelle",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0033365",
                        description="Translocation across the double membrane of mitochondrion-related organelles and presequence cleavage by processing peptidase",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0032047",
                        label="mitosome",
                        node_type="CELLULAR_LOCALIZATION",
                        grounding="GO:0032047",
                        description="Double-membrane mitochondrion-related organelle of anaerobic eukaryotes such as Giardia intestinalis that functions in iron-sulfur cluster assembly",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0042566",
                        label="hydrogenosome",
                        node_type="CELLULAR_LOCALIZATION",
                        grounding="GO:0042566",
                        description="Hydrogen-producing double-membrane mitochondrion-related organelle of anaerobic eukaryotes such as Trichomonas vaginalis",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="SO:0000725",
                        predicate="RO:0002331",
                        predicate_label="involved in",
                        object="GO:0033365",
                        description="N-terminal targeting signals on mitosomal and hydrogenosomal precursor proteins are necessary and sufficient for recognition by the organellar import and processing peptidase machinery.",
                        reference="PMID:16040811",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "Here, we report that proteins targeted into mitosomes of Giardia "
                            "intestinalis have targeting signals necessary and sufficient to be "
                            "recognized by the mitosomal protein import machinery."
                        ),
                        notes="N-terminal targeting presequences direct import into mitosomes and hydrogenosomes (PMID:16040811).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0033365",
                        predicate="RO:0002339",
                        predicate_label="has target end location",
                        object="GO:0032047",
                        description="Mitosomal protein import machinery recognizes the N-terminal presequence and delivers the imported protein into mitosomes.",
                        reference="PMID:16040811",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "Here, we report that proteins targeted into mitosomes of Giardia "
                            "intestinalis have targeting signals necessary and sufficient to be "
                            "recognized by the mitosomal protein import machinery."
                        ),
                        notes="Presequence-directed import into Giardia mitosomes (PMID:16040811).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0033365",
                        predicate="RO:0002339",
                        predicate_label="has target end location",
                        object="GO:0042566",
                        description="Shared presequence recognition and inner-membrane translocase/peptidase processing deliver precursor proteins into hydrogenosomes.",
                        reference="PMID:16040811",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "Expression of these mitosomal proteins in Trichomonas vaginalis "
                            "results in targeting to hydrogenosomes, a hydrogen-producing form "
                            "of mitochondria."
                        ),
                        notes="Cross-recognition and import into hydrogenosomes (PMID:16040811).",
                    ),
                ),
            ),
        ),
    ),
    # --- 16. SEQ_PROPEPTIDE additions (2 records) ---
    TraitSpec(
        rel_dir="sequence/propeptide",
        filename="vitamin-k-dependent-gamma-carboxylation-recognition-propeptide.yaml",
        identifier="proteintraitsmech:PROPEPTIDE_VKD_GLA_RECOGNITION",
        label="vitamin K-dependent gamma-carboxylation recognition propeptide",
        definition=(
            "A cleavable N-terminal propeptide (typically residues -18 to -1, carrying conserved "
            "Phe-16 and Ala-10 recognition determinants) in vitamin K-dependent coagulation and "
            "calcification precursor proteins (such as Factor IX, Factor X, prothrombin, "
            "Protein C, and osteocalcin) that functions as an obligate exosite docking motif "
            "for vitamin K-dependent gamma-glutamyl carboxylase (GGCX, GO:0008488) in the "
            "endoplasmic reticulum, directing processive gamma-carboxylation of downstream "
            "glutamate residues into L-gamma-carboxyglutamic acid (Gla, MOD:00041) prior to "
            "propeptide excision in the trans-Golgi."
        ),
        trait_axis="SEQUENCE",
        trait_category="SEQ_PROPEPTIDE",
        parent_traits=("proteintraitsmech:UNIPROT_FT_SEQ_PROPEPTIDE",),
        synonyms=(
            ("gamma-glutamyl carboxylase docking propeptide", "EXACT_SYNONYM"),
            ("Gla-domain carboxylation recognition propeptide", "EXACT_SYNONYM"),
            ("VKD propeptide", "RELATED_SYNONYM"),
        ),
        xrefs=("SO:0001062", "GO:0008488", "GO:0017187", "MOD:00041"),
        evidence=(
            (
                "PMID:3802193",
                "The propeptide of Factor IX (residues -18 to -1, including Phe-16 and Ala-10) defines the recognition site that designates the adjacent glutamic acid-rich domain for vitamin K-dependent gamma-carboxylation.",
            ),
        ),
        detection_methods=(M_PROPEP,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="CG_PROPEPTIDE_VKD_GLA_RECOGNITION",
                label="Propeptide exosite recognition directs vitamin K-dependent gamma-glutamyl carboxylation",
                mechanism_summary=(
                    "The vitamin K-dependent recognition propeptide (SO:0001062) docks to "
                    "gamma-glutamyl carboxylase (GO:0008488), positively regulating "
                    "peptidyl-glutamic acid carboxylation (GO:0017187) of the adjacent Gla "
                    "domain to generate L-gamma-carboxyglutamic acid residues (MOD:00041)."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="SO:0001062",
                        label="propeptide",
                        node_type="MOTIF",
                        grounding="SO:0001062",
                        description="Conserved N-terminal propeptide (residues -18 to -1) that tethers vitamin K-dependent precursors to gamma-glutamyl carboxylase",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0008488",
                        label="gamma-glutamyl carboxylase activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0008488",
                        description="Vitamin K-dependent gamma-glutamyl carboxylase (GGCX) activity converting glutamate residues to gamma-carboxyglutamate",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0017187",
                        label="peptidyl-glutamic acid carboxylation",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0017187",
                        description="Post-translational gamma-carboxylation of glutamic acid residues in the adjacent Gla domain",
                    ),
                    CausalNodeSpec(
                        node_id="MOD:00041",
                        label="L-gamma-carboxyglutamic acid",
                        node_type="PTM",
                        grounding="MOD:00041",
                        description="Calcium-coordinating L-gamma-carboxyglutamic acid (Gla) residue produced in the mature vitamin K-dependent domain",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="SO:0001062",
                        predicate="RO:0002213",
                        predicate_label="positively regulates",
                        object="GO:0008488",
                        description="The conserved N-terminal propeptide (including Phe-16 and Ala-10) provides the recognition site required for gamma-glutamyl carboxylase recruitment.",
                        reference="PMID:3802193",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "These results indicate that the Factor IX propeptide participates "
                            "in defining a recognition site that designates an adjacent glutamic "
                            "acid-rich domain for gamma-carboxylation."
                        ),
                        notes="Factor IX propeptide defines the recognition site for gamma-carboxylation (PMID:3802193).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0008488",
                        predicate="RO:0002213",
                        predicate_label="positively regulates",
                        object="GO:0017187",
                        description="Propeptide-bound gamma-glutamyl carboxylase catalyzes processive peptidyl-glutamic acid carboxylation.",
                        reference="PMID:3802193",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "Deletion of the propeptide (residues -18 to -1) abolished "
                            "carboxylation, but not secretion, of Factor IX."
                        ),
                        notes="Deletion of the propeptide abolishes gamma-carboxylation (PMID:3802193).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0017187",
                        predicate="RO:0002234",
                        predicate_label="has output",
                        object="MOD:00041",
                        description="Peptidyl-glutamic acid carboxylation converts specific glutamate residues into L-gamma-carboxyglutamic acid (Gla).",
                        reference="PMID:3802193",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "Posttranslational processing of vitamin K-dependent proteins "
                            "includes gamma-carboxylation of specific glutamic acid residues to "
                            "form gamma-carboxyglutamic acids."
                        ),
                        notes="Gamma-carboxylation forms gamma-carboxyglutamic acid residues (PMID:3802193).",
                    ),
                ),
            ),
        ),
    ),
    TraitSpec(
        rel_dir="sequence/propeptide",
        filename="gpi-anchor-c-terminal-propeptide.yaml",
        identifier="proteintraitsmech:PROPEPTIDE_GPI_C_TERMINAL",
        label="GPI-anchor C-terminal transamidase-cleaved propeptide",
        definition=(
            "A transient C-terminal propeptide extension (spanning the polar spacer downstream "
            "of the omega cleavage site and a C-terminal hydrophobic tail) on precursor proteins "
            "destined for glycosylphosphatidylinositol (GPI) anchoring that is recognized and "
            "cleaved at the omega residue in the endoplasmic reticulum lumen by the "
            "heteropentameric GPI-anchor transamidase complex (PIGK/GPAA1/PIGT/PIGS/PIGU, "
            "GO:0003923) concomitant with amide-bond transfer of the mature C-terminus onto a "
            "preassembled GPI glycolipid anchor."
        ),
        trait_axis="SEQUENCE",
        trait_category="SEQ_PROPEPTIDE",
        parent_traits=("proteintraitsmech:UNIPROT_FT_SEQ_PROPEPTIDE",),
        synonyms=(
            ("C-terminal GPI-attachment propeptide signal", "EXACT_SYNONYM"),
            ("omega-site C-terminal propeptide", "EXACT_SYNONYM"),
            ("GPI-T cleaved C-terminal peptide", "RELATED_SYNONYM"),
        ),
        xrefs=("SO:0001062", "GO:0003923", "GO:0016255", "GO:0051604", "GO:0042765"),
        evidence=(
            (
                "PMID:35165458",
                "Attachment of GPI anchors to precursor proteins in the ER is catalyzed by the five-subunit transmembrane GPI transamidase (GPIT) complex via the PIGK Cys206-His164-Asn58 catalytic triad.",
            ),
        ),
        detection_methods=(M_PROPEP,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="CG_PROPEPTIDE_GPI_C_TERMINAL",
                label="GPI-anchor transamidase cleavage of C-terminal propeptide and GPI attachment",
                mechanism_summary=(
                    "The C-terminal GPI propeptide extension (SO:0001062) positions the "
                    "precursor omega site in the catalytic cleft of the PIGK subunit within "
                    "the GPI-anchor transamidase complex (GO:0003923), which cleaves off the "
                    "C-terminal propeptide and catalyzes attachment of the GPI anchor to the "
                    "protein (GO:0016255), driving endoplasmic-reticulum protein maturation "
                    "(GO:0051604)."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="SO:0001062",
                        label="propeptide",
                        node_type="MOTIF",
                        grounding="SO:0001062",
                        description="Transient C-terminal hydrophobic propeptide downstream of the omega site cleaved during GPI transamidation",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0003923",
                        label="GPI-anchor transamidase activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0003923",
                        description="Catalytic activity of the GPI transamidase complex (PIGK Cys206-His164-Asn58 triad) cleaving the omega-site peptide bond and transferring the GPI anchor",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0016255",
                        label="attachment of GPI anchor to protein",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0016255",
                        description="Endoplasmic-reticulum covalent replacement of the C-terminal propeptide with a preassembled GPI glycolipid anchor",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0051604",
                        label="protein maturation",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0051604",
                        description="Maturation of GPI-anchored precursor proteins in the endoplasmic reticulum prior to cell-surface transport",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="SO:0001062",
                        predicate="RO:0000056",
                        predicate_label="participates in",
                        object="GO:0003923",
                        description="The C-terminal propeptide participates as the cleavage/transfer substrate at the PIGK Cys206-His164-Asn58 catalytic triad of GPI transamidase.",
                        reference="PMID:35165458",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "The PIGK subunit functions as the catalytic component, in which we "
                            "identified a C206-H164-N58 triad that is critical for the "
                            "transamination reaction."
                        ),
                        notes="PIGK Cys206-His164-Asn58 catalytic triad drives the GPI transamidation cleavage/transfer reaction (PMID:35165458).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0003923",
                        predicate="RO:0002213",
                        predicate_label="positively regulates",
                        object="GO:0016255",
                        description="GPI-anchor transamidase cleavage of the C-terminal propeptide catalyzes covalent attachment of the GPI anchor in the ER.",
                        reference="PMID:35165458",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "Attaching GPI to the protein in the endoplasmic reticulum (ER) is "
                            "catalyzed by the transmembrane GPI transamidase (GPIT) complex, "
                            "which is essential for maturation of the GPI-anchored proteins."
                        ),
                        notes="GPIT complex catalyzes GPI attachment in the ER (PMID:35165458).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0016255",
                        predicate="RO:0002411",
                        predicate_label="causally upstream of",
                        object="GO:0051604",
                        description="Covalent GPI-anchor attachment in the ER is essential for the maturation of GPI-anchored proteins.",
                        reference="PMID:35165458",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "Attaching GPI to the protein in the endoplasmic reticulum (ER) is "
                            "catalyzed by the transmembrane GPI transamidase (GPIT) complex, "
                            "which is essential for maturation of the GPI-anchored proteins."
                        ),
                        notes="GPI attachment is essential for maturation of GPI-anchored proteins (PMID:35165458).",
                    ),
                ),
            ),
        ),
    ),
    # --- 17. STRUCT_CAVITY additions (2 records) ---
    TraitSpec(
        rel_dir="structure/cavity",
        filename="transmembrane-ion-channel-selectivity-filter-pore.yaml",
        identifier="proteintraitsmech:CAVITY_SELECTIVITY_FILTER_PORE",
        label="transmembrane ion-channel selectivity-filter pore",
        definition=(
            "A specialized transmembrane channel cavity architecture consisting of a wide, "
            "water-filled central vestibule coupled to a narrow (~12 A long) constricted "
            "selectivity filter lined by backbone carbonyl oxygens or side-chain coordination "
            "rings that mimic the hydration shell of a specific permeant ion (such as K+, Na+, "
            "or Ca2+), enabling rapid, near-diffusion-limited conduction with high ionic "
            "selectivity."
        ),
        trait_axis="STRUCTURE",
        trait_category="STRUCT_CAVITY",
        parent_traits=("proteintraitsmech:CAVITY", "proteintraitsmech:TUNNEL"),
        synonyms=(
            ("ion channel selectivity filter pore", "EXACT_SYNONYM"),
            ("transmembrane conduction pore with selectivity filter", "EXACT_SYNONYM"),
            ("selectivity filter and central cavity", "RELATED_SYNONYM"),
        ),
        xrefs=("SO:0000417", "GO:0046872", "GO:0005216", "GO:0034220"),
        evidence=(
            (
                "PMID:9525859",
                "The KcsA potassium channel pore comprises a wide water-filled central cavity and a narrow 12-angstrom selectivity filter lined by main-chain carbonyl oxygens that coordinate dehydrated K+ ions for selective conduction.",
            ),
        ),
        detection_methods=(M_CAVER,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="CG_CAVITY_SELECTIVITY_FILTER_PORE",
                label="Backbone carbonyl coordination and multi-ion repulsion in the selectivity-filter pore drive selective ion conduction",
                mechanism_summary=(
                    "The pore-lining selectivity-filter polypeptide domain (SO:0000417) holds "
                    "backbone carbonyl oxygens at precise coordination distances to enable "
                    "selective metal ion binding (GO:0046872) that dehydrates and coordinates "
                    "permeant ions while excluding non-cognate ions, which is causally upstream "
                    "of monoatomic ion channel activity (GO:0005216) and positively regulates "
                    "monoatomic ion transmembrane transport (GO:0034220)."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="SO:0000417",
                        label="polypeptide_domain",
                        node_type="DOMAIN",
                        grounding="SO:0000417",
                        description="Pore-lining transmembrane selectivity-filter domain combining a central water-filled cavity with a narrow 12-A carbonyl-lined filter",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0046872",
                        label="metal ion binding",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0046872",
                        description="Dehydrated metal ion coordination by the rings of main-chain carbonyl oxygen atoms lining the 12-A selectivity filter",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0005216",
                        label="monoatomic ion channel activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0005216",
                        description="Selective catalysis of facilitated diffusion of monoatomic ions through a transmembrane aqueous pore",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0034220",
                        label="monoatomic ion transmembrane transport",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0034220",
                        description="Selective conduction of monoatomic ions across the lipid bilayer driven by multi-ion electrostatic repulsion",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="SO:0000417",
                        predicate="RO:0002327",
                        predicate_label="enables",
                        object="GO:0046872",
                        description="Structurally constrained main-chain carbonyl oxygens in the selectivity-filter domain coordinate dehydrated K+ ions while excluding smaller Na+ ions.",
                        reference="PMID:9525859",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "Main chain carbonyl oxygen atoms from the K+ channel signature "
                            "sequence line the selectivity filter, which is held open by "
                            "structural constraints to coordinate K+ ions but not smaller Na+ ions."
                        ),
                        notes="Selectivity filter carbonyl geometry coordinates K+ selectively (PMID:9525859).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0046872",
                        predicate="RO:0002411",
                        predicate_label="causally upstream of",
                        object="GO:0005216",
                        description="Selective coordination of permeant ions in the filter pore drives selective monoatomic ion channel activity.",
                        reference="PMID:9525859",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "Main chain carbonyl oxygen atoms from the K+ channel signature "
                            "sequence line the selectivity filter, which is held open by "
                            "structural constraints to coordinate K+ ions but not smaller Na+ ions."
                        ),
                        notes="Carbonyl-lined selectivity filter enables selective monoatomic ion channel activity (PMID:9525859).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0005216",
                        predicate="RO:0002213",
                        predicate_label="positively regulates",
                        object="GO:0034220",
                        description="Electrostatic repulsion between simultaneously bound ions in the selectivity filter promotes rapid transmembrane ion conduction.",
                        reference="PMID:9525859",
                        evidence_code="ECO:0000269",
                        snippet=(
                            "This configuration promotes ion conduction by exploiting "
                            "electrostatic repulsive forces to overcome attractive forces "
                            "between K+ ions and the selectivity filter."
                        ),
                        notes="Multi-ion electrostatic repulsion drives rapid selective conduction (PMID:9525859).",
                    ),
                ),
            ),
        ),
    ),
    TraitSpec(
        rel_dir="structure/cavity",
        filename="buried-active-site-substrate-access-tunnel.yaml",
        identifier="proteintraitsmech:CAVITY_SUBSTRATE_ACCESS_TUNNEL",
        label="buried active-site substrate/product access tunnel",
        definition=(
            "An internal structural tunnel connecting a deeply buried enzyme catalytic cavity "
            "to the bulk exterior solvent, characterized by a bottleneck radius, length, "
            "curvature, and gating residue lining that control substrate ingress, water/cosubstrate "
            "access, reaction-intermediate shielding, and product egress."
        ),
        trait_axis="STRUCTURE",
        trait_category="STRUCT_CAVITY",
        parent_traits=("proteintraitsmech:CAVITY", "proteintraitsmech:TUNNEL"),
        synonyms=(
            ("enzyme active-site access tunnel", "EXACT_SYNONYM"),
            ("substrate ingress / product egress tunnel", "EXACT_SYNONYM"),
            ("gated catalytic access channel", "RELATED_SYNONYM"),
        ),
        xrefs=("CHEBI:24431", "GO:0036094", "GO:0003824", "GO:0008152"),
        evidence=(
            (
                "PMID:23093919",
                "Tunnels and channels facilitate the transport of small molecules, ions, and water solvent between buried enzyme active sites and bulk solvent, governing substrate specificity and catalytic efficiency.",
            ),
        ),
        detection_methods=(M_CAVER,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="CG_CAVITY_SUBSTRATE_ACCESS_TUNNEL",
                label="Internal access tunnel geometry governs small-molecule exchange with buried catalytic sites",
                mechanism_summary=(
                    "A buried active-site access tunnel provides the internal transport pathway "
                    "for small-molecule substrates, ions, and solvent (CHEBI:24431) to reach and "
                    "depart the occluded catalytic pocket, enabling small molecule binding "
                    "(GO:0036094), regulating enzyme catalytic activity (GO:0003824), and "
                    "supporting cellular metabolic processes (GO:0008152)."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="CHEBI:24431",
                        label="chemical entity",
                        node_type="LIGAND",
                        grounding="CHEBI:24431",
                        description="Small-molecule substrates, ions, and water solvent transported through the internal access tunnel",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0036094",
                        label="small molecule binding",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0036094",
                        description="Transport and binding of small-molecule substrates and ligands into the buried enzyme active site",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0003824",
                        label="catalytic activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0003824",
                        description="Enzyme catalysis within the buried active-site cavity governed by tunnel bottleneck geometry and gating kinetics",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0008152",
                        label="metabolic process",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0008152",
                        description="Enzymatic metabolic conversions mediated by biocatalysts with buried active-site tunnels",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="CHEBI:24431",
                        predicate="RO:0002331",
                        predicate_label="involved in",
                        object="GO:0036094",
                        description="Internal protein tunnels facilitate the transport of small-molecule substrates, ions, and water between bulk solvent and buried binding sites.",
                        reference="PMID:23093919",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Tunnels and channels facilitate the transport of small molecules, "
                            "ions and water solvent in a large variety of proteins."
                        ),
                        notes="Tunnels facilitate small-molecule and solvent transport in proteins (PMID:23093919).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0036094",
                        predicate="RO:0002213",
                        predicate_label="positively regulates",
                        object="GO:0003824",
                        description="Pathway geometry, physicochemical lining, and dynamics of substrate/product transport pathways govern enzyme structure-function and catalytic activity.",
                        reference="PMID:23093919",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Characteristics of individual transport pathways, including their "
                            "geometry, physico-chemical properties and dynamics are instrumental "
                            "for understanding of structure-function relationships of these "
                            "proteins, for the design of new inhibitors and construction of "
                            "improved biocatalysts."
                        ),
                        notes="Tunnel geometry and dynamics govern enzyme catalytic function (PMID:23093919).",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0003824",
                        predicate="RO:0002213",
                        predicate_label="positively regulates",
                        object="GO:0008152",
                        description="Biocatalytic turnover in enzymes with buried active-site access tunnels drives metabolic transformations.",
                        reference="PMID:23093919",
                        evidence_code="ECO:0000305",
                        snippet=(
                            "Characteristics of individual transport pathways, including their "
                            "geometry, physico-chemical properties and dynamics are instrumental "
                            "for understanding of structure-function relationships of these "
                            "proteins, for the design of new inhibitors and construction of "
                            "improved biocatalysts."
                        ),
                        notes="Biocatalytic function enabled by buried active-site tunnels (PMID:23093919).",
                    ),
                ),
            ),
        ),
    ),
    # --- 18. EVO_CONSERVATION additions (3 records) ---
    TraitSpec(
        rel_dir="evolution/conservation",
        filename="universal-single-copy-ortholog-protein.yaml",
        identifier="proteintraitsmech:EVO_UNIVERSAL_SINGLE_COPY_ORTHOLOG",
        label="universal single-copy ortholog protein",
        definition=(
            "An evolutionary protein conservation trait in which a protein-coding gene is "
            "maintained as a strictly single-copy orthologous group present in >= 90% of "
            "species across a broad taxonomic clade (such as Bacteria, Archaea, or Eukaryota; "
            "BUSCO / OrthoDB universal single-copy markers), reflecting strong dosage-balance "
            "and functional constraints against both gene loss and paralogous duplication."
        ),
        trait_axis="EVOLUTION",
        trait_category="EVO_CONSERVATION",
        parent_traits=("proteintraitsmech:EVO_CONSERVED",),
        synonyms=(
            ("BUSCO single-copy ortholog", "EXACT_SYNONYM"),
            ("universal single-copy marker protein", "EXACT_SYNONYM"),
            ("dosage-constrained universal ortholog", "RELATED_SYNONYM"),
        ),
        evidence=(
            (
                "PMID:26059717",
                "Benchmarking Universal Single-Copy Orthologs (BUSCO) defines clade-wide orthologous protein groups present as single-copy genes in >90% of species due to evolutionary constraints on gene content and duplication.",
            ),
        ),
        detection_methods=(M_BUSCO,),
        evolutionary_scope=(
            ("min_prevalence", 0.9),
            ("max_prevalence", 1.0),
            ("definition_method", "BUSCO / OrthoDB universal single-copy ortholog benchmark (>=90% single-copy presence)"),
            ("conservation_metric", "presence-breadth (single-copy across >=90% of species in clade)"),
            ("orthology_basis", "OrthoDB / BUSCO profile-HMM orthologous groups"),
        ),
    ),
    TraitSpec(
        rel_dir="evolution/conservation",
        filename="purifying-selection-constrained-protein.yaml",
        identifier="proteintraitsmech:EVO_PURIFYING_SELECTION_CONSTRAINED",
        label="purifying-selection-constrained protein (dN/dS << 1)",
        definition=(
            "An evolutionary protein conservation regime characterized by a ratio of "
            "nonsynonymous to synonymous substitution rates significantly below unity "
            "(omega = dN/dS << 1, typically omega < 0.2 across coding alignments), indicating "
            "pervasive negative (purifying) Darwinian selection that eliminates deleterious "
            "amino-acid replacements to preserve fold stability, catalytic geometry, or "
            "interaction interfaces."
        ),
        trait_axis="EVOLUTION",
        trait_category="EVO_CONSERVATION",
        parent_traits=("proteintraitsmech:EVO_CONSERVED",),
        synonyms=(
            ("negatively selected protein", "EXACT_SYNONYM"),
            ("low dN/dS constrained protein", "EXACT_SYNONYM"),
            ("purifying Darwinian selection regime", "RELATED_SYNONYM"),
        ),
        evidence=(
            (
                "PMID:17483113",
                "Maximum-likelihood codon substitution models in PAML estimate nonsynonymous and synonymous substitution rates (dN and dS) to quantify purifying selection (dN/dS < 1) across protein-coding alignments.",
            ),
        ),
        detection_methods=(M_CODEML_HYPHY,),
        evolutionary_scope=(
            ("definition_method", "PAML codeml / HyPhy maximum-likelihood codon substitution model (omega = dN/dS << 1)"),
            ("conservation_metric", "dN/dS (purifying selection, omega < 1)"),
            ("orthology_basis", "codon-aligned orthologous coding sequences"),
        ),
    ),
    TraitSpec(
        rel_dir="evolution/conservation",
        filename="positively-selected-diversifying-protein.yaml",
        identifier="proteintraitsmech:EVO_POSITIVELY_SELECTED_DIVERSIFYING",
        label="positively selected diversifying protein (dN/dS > 1)",
        definition=(
            "An evolutionary protein regime characterized by an elevated nonsynonymous-to-synonymous "
            "substitution rate ratio exceeding unity (omega = dN/dS > 1 across the coding "
            "sequence or at specific foreground branches/codon sites), driven by positive "
            "(diversifying) Darwinian selection for adaptive sequence innovation such as "
            "host-pathogen arms races, immune evasion, toxin diversification, or novel "
            "substrate recognition."
        ),
        trait_axis="EVOLUTION",
        trait_category="EVO_CONSERVATION",
        parent_traits=("proteintraitsmech:EVO_VARIABLE",),
        synonyms=(
            ("diversifying selection protein", "EXACT_SYNONYM"),
            ("adaptively evolving protein (omega > 1)", "EXACT_SYNONYM"),
            ("positive Darwinian selection protein", "EXACT_SYNONYM"),
        ),
        evidence=(
            (
                "PMID:17483113",
                "Maximum-likelihood phylogenetic comparison of protein-coding genes in PAML detects positive Darwinian selection where the nonsynonymous substitution rate exceeds the synonymous rate (omega = dN/dS > 1).",
            ),
        ),
        detection_methods=(M_CODEML_HYPHY,),
        evolutionary_scope=(
            ("definition_method", "PAML codeml / HyPhy branch-site or site-wise codon substitution model (omega = dN/dS > 1)"),
            ("conservation_metric", "dN/dS (positive diversifying selection, omega > 1)"),
            ("orthology_basis", "codon-aligned orthologous coding sequences"),
        ),
    ),
    # --- 16. Cycle 3 Stage 1 expansion across SEQ_LOW_COMPLEXITY, SEQ_INITIATOR_METHIONINE,
    #         SEQ_MATURE_CHAIN, STRUCT_ALLOSTERIC_SITE, STRUCT_DISULFIDE, STRUCT_SURFACE,
    #         and STRUCT_DYNAMICS (17 records) ---
    TraitSpec(
        rel_dir="sequence/low_complexity",
        filename="polyampholytic-mixed-charge-block-low-complexity-region.yaml",
        identifier="proteintraitsmech:LOWCOMP_POLYAMPHOLYTIC_CHARGE_BLOCK",
        label="polyampholytic mixed-charge-block low-complexity region",
        definition=(
            "A low-complexity sequence region enriched in both positively charged (Lys, Arg) "
            "and negatively charged (Glu, Asp) residues arranged in alternating or segregated "
            "charge blocks (quantified by the charge-patterning parameter kappa or sequential "
            "charge decoration SCD), governing chain compaction, alpha-helical single-alpha-helix "
            "formation, or electrostatic coacervation and nuclear-speckle partitioning."
        ),
        trait_axis="SEQUENCE",
        trait_category="SEQ_LOW_COMPLEXITY",
        parent_traits=("proteintraitsmech:LOWCOMP_REGION",),
        synonyms=(
            ("charge-blocky polyampholytic low-complexity region", "EXACT_SYNONYM"),
            ("high-kappa mixed-charge low-complexity tract", "RELATED_SYNONYM"),
            ("E/K or D/R alternating charge block domain", "RELATED_SYNONYM"),
        ),
        evidence=(
            (
                "PMID:23901099",
                "Conformations of intrinsically disordered polyampholytic proteins are governed by the fraction of charged residues and the linear sequence patterning of oppositely charged residues.",
            ),
            (
                "PMID:28851299",
                "fLPS identifies multi-residue charged compositional biases and low-complexity regions in protein sequences.",
            ),
        ),
        detection_methods=(M_FLPS, M_SEG),
    ),
    TraitSpec(
        rel_dir="sequence/low_complexity",
        filename="phenylalanine-glycine-fg-repeat-low-complexity-region.yaml",
        identifier="proteintraitsmech:LOWCOMP_FG_NUCLEOPORIN_REPEAT_REGION",
        label="phenylalanine-glycine (FG)-repeat low-complexity region",
        definition=(
            "A low-complexity intrinsically disordered sequence region composed of tandem "
            "phenylalanine-glycine dipeptide motifs (including FG, FxFG, GLFG, and PAFG repeats) "
            "separated by polar or charged spacer sequences, characteristic of nuclear pore "
            "complex FG-nucleoporins where cohesive hydrophobic Phe-Phe interactions form a "
            "selective hydrogel-like permeability barrier penetrated by karyopherin transport receptors."
        ),
        trait_axis="SEQUENCE",
        trait_category="SEQ_LOW_COMPLEXITY",
        parent_traits=("proteintraitsmech:LOWCOMP_REGION",),
        synonyms=(
            ("FG-repeat nucleoporin domain", "EXACT_SYNONYM"),
            ("GLFG / FxFG repeat low-complexity region", "NARROW_SYNONYM"),
            ("cohesive FG-repeat hydrogel domain", "RELATED_SYNONYM"),
        ),
        sequence_pattern="(?:F[A-Z]?FG|GLFG|[PA]FG)",
        evidence=(
            (
                "PMID:17082456",
                "Phenylalanine-mediated inter-repeat interactions cross-link Phe and Gly (FG)-rich nucleoporin repeat domains into elastic and reversible hydrogels that form the selective nuclear pore permeability barrier.",
            ),
            (
                "PMID:28851299",
                "fLPS detects multiple-residue compositional biases including Phe/Gly-rich low-complexity regions.",
            ),
        ),
        detection_methods=(M_SEG, M_FLPS),
    ),
    TraitSpec(
        rel_dir="sequence/initiator_methionine",
        filename="initiator-methionine-ac-n-degron-and-arg-n-degron-site.yaml",
        identifier="proteintraitsmech:INIT_METHIONINE_N_DEGRON",
        label="initiator-methionine N-degron recognition site",
        definition=(
            "A retained N-terminal initiator methionine site that functions as a conditional "
            "proteolytic degradation signal (N-degron) in the ubiquitin-dependent N-end rule "
            "pathway, either after co-translational N-alpha-acetylation (Ac/N-degron recognized "
            "by Doa10/MARCH6 when unshielded by partner subunits) or when retained unmodified "
            "ahead of a bulky hydrophobic penultimate residue (MPhi Arg/N-degron recognized by "
            "UBR-family E3 ubiquitin ligases)."
        ),
        trait_axis="SEQUENCE",
        trait_category="SEQ_INITIATOR_METHIONINE",
        parent_traits=("proteintraitsmech:INIT_METHIONINE_RETAINED",),
        synonyms=(
            ("Ac/N-degron initiator methionine site", "NARROW_SYNONYM"),
            ("MPhi/N-degron retained Met1 site", "NARROW_SYNONYM"),
            ("N-end rule initiator methionine degradation signal", "EXACT_SYNONYM"),
        ),
        xrefs=("SO:0000419", "MOD:00058"),
        evidence=(
            (
                "PMID:20110468",
                "Retained and N-terminally acetylated initiator methionine residues act as specific Ac/N-degron degradation signals targeted by the Doa10/MARCH6 ubiquitin ligase in the N-end rule pathway.",
            ),
        ),
        detection_methods=(M_NAT_PRED, M_MAP_NME_RETAINED),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="CG_INIT_METHIONINE_N_DEGRON",
                label="N-terminally acetylated retained initiator methionine functions as an Ac/N-degron recognized by E3 ubiquitin ligases for proteasomal degradation",
                mechanism_summary=(
                    "Co-translational retention and N-alpha-acetylation of the initiator methionine "
                    "residue creates a conditional Ac/N-degron recognized by N-recognin E3 "
                    "ubiquitin-protein transferases (such as Doa10/MARCH6), driving ubiquitin-dependent "
                    "protein catabolism via the N-end rule pathway and 26S proteasomal degradation."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="MOD:00058",
                        label="N-acetyl-L-methionine",
                        node_type="PTM",
                        grounding="MOD:00058",
                        description="Retained N-terminal initiator L-methionine residue modified by N-alpha-acetylation to form an Ac/N-degron.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0004842",
                        label="ubiquitin-protein transferase activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0004842",
                        description="E3 ubiquitin ligase N-recognin activity (e.g. Doa10/MARCH6) that recognizes the unshielded N-acetylated initiator methionine.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0071596",
                        label="ubiquitin-dependent protein catabolic process via the N-end rule pathway",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0071596",
                        description="Selective polyubiquitination and turnover of proteins bearing destabilizing N-terminal degradation signals (N-degrons).",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0043161",
                        label="proteasome-mediated ubiquitin-dependent protein catabolic process",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0043161",
                        description="Proteolytic degradation of the polyubiquitinated N-degron substrate by the 26S proteasome.",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="MOD:00058",
                        predicate="RO:0000056",
                        predicate_label="participates in",
                        object="GO:0004842",
                        description="The N-acetylated initiator methionine (Ac/N-degron) is recognized as a substrate determinant by the Doa10 E3 ubiquitin-protein transferase.",
                        reference="PMID:20110468",
                        evidence_code="ECO:0000269",
                        snippet="Using the yeast Saccharomyces cerevisiae, we found that the Nt-acetylated Met residue could act as a degradation signal (degron), targeted by the Doa10 ubiquitin ligase.",
                        notes="Hwang et al. 2010 demonstrate that Nt-acetylated Met acts as an Ac/N-degron recognized by the Doa10 ubiquitin ligase.",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0004842",
                        predicate="RO:0002213",
                        predicate_label="positively regulates",
                        object="GO:0071596",
                        description="Recognition and polyubiquitination by the N-recognin E3 ubiquitin-protein transferase drives ubiquitin-dependent catabolism via the N-end rule pathway.",
                        reference="PMID:20110468",
                        evidence_code="ECO:0000269",
                        snippet="Using the yeast Saccharomyces cerevisiae, we found that the Nt-acetylated Met residue could act as a degradation signal (degron), targeted by the Doa10 ubiquitin ligase.",
                        notes="Doa10-mediated ubiquitination of Nt-acetylated Met initiates the Ac/N-end rule proteolytic pathway.",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0071596",
                        predicate="RO:0002411",
                        predicate_label="causally upstream of",
                        object="GO:0043161",
                        description="Ubiquitin-dependent N-end rule targeting commits the unshielded Ac/N-degron-bearing protein to proteasome-mediated degradation.",
                        reference="PMID:20110468",
                        evidence_code="ECO:0000269",
                        snippet="The retained N-terminal methionine (Met) residue of a nascent protein is often N-terminally acetylated (Nt-acetylated).",
                        notes="N-end rule polyubiquitination of Nt-acetylated nascent chains leads to proteasomal degradation.",
                    ),
                ),
            ),
        ),
    ),
    TraitSpec(
        rel_dir="sequence/mature_chain",
        filename="autocatalytically-cleaved-mature-polypeptide-chain.yaml",
        identifier="proteintraitsmech:MATURE_CHAIN_AUTOCATALYTIC_CLEAVED",
        label="autocatalytically cleaved mature polypeptide chain",
        definition=(
            "A mature polypeptide chain generated by intramolecular cis-autoproteolytic "
            "cleavage of a precursor zymogen without an external protease, typically via "
            "an N->O or N->S acyl rearrangement catalyzed by an internal threonine, serine, "
            "or cysteine residue that becomes the catalytic N-terminal nucleophile (as in "
            "Ntn-hydrolases such as proteasome beta subunits, penicillin acylase, glycosylasparaginase, "
            "and GPCR autoproteolysis-inducing GAIN domains)."
        ),
        trait_axis="SEQUENCE",
        trait_category="SEQ_MATURE_CHAIN",
        parent_traits=("proteintraitsmech:UNIPROT_FT_SEQ_MATURE_CHAIN",),
        synonyms=(
            ("Ntn-hydrolase autoproteolytically processed mature chain", "NARROW_SYNONYM"),
            ("cis-autoproteolytic mature polypeptide subunit", "EXACT_SYNONYM"),
            ("self-cleaved N-terminal nucleophile mature chain", "RELATED_SYNONYM"),
        ),
        xrefs=("SO:0000419",),
        evidence=(
            (
                "PMID:7477383",
                "N-terminal nucleophile (Ntn) hydrolases share a beta-sandwich fold that catalyzes intramolecular autocatalytic processing of an inactive precursor to liberate a mature chain with a catalytic N-terminal Thr, Ser, or Cys nucleophile.",
            ),
        ),
        detection_methods=(M_PROPEP,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="CG_MATURE_CHAIN_AUTOCATALYTIC_CLEAVED",
                label="Intramolecular cis-autoproteolytic cleavage liberates a mature polypeptide chain bearing a catalytic N-terminal nucleophile",
                mechanism_summary=(
                    "In N-terminal nucleophile (Ntn) hydrolases and related autoproteolytic zymogens, "
                    "the folded precursor catalyzes intramolecular proteolysis at the peptide bond "
                    "preceding an internal Thr, Ser, or Cys residue, liberating a mature polypeptide "
                    "chain whose newly exposed N-terminal residue serves as the active-site nucleophile."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="GO:0006508",
                        label="proteolysis",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0006508",
                        description="Intramolecular cis-autoproteolytic cleavage of the scissile peptide bond preceding the catalytic nucleophile.",
                    ),
                    CausalNodeSpec(
                        node_id="SO:0000419",
                        label="mature_protein_region",
                        node_type="DOMAIN",
                        grounding="SO:0000419",
                        description="Processed mature polypeptide chain carrying a newly liberated N-terminal Thr, Ser, or Cys nucleophile.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0051604",
                        label="protein maturation",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0051604",
                        description="Conversion of the inactive single-chain zymogen precursor into the mature active enzyme subunit.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0003824",
                        label="catalytic activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0003824",
                        description="Active-site nucleophilic catalysis enabled by the free alpha-amino group and side chain of the N-terminal residue of the mature chain.",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="GO:0006508",
                        predicate="RO:0002234",
                        predicate_label="has output",
                        object="SO:0000419",
                        description="Intramolecular autocatalytic proteolysis cleaves the precursor to yield the mature polypeptide chain.",
                        reference="PMID:7477383",
                        evidence_code="ECO:0000269",
                        snippet="This fold provides both the capacity for nucleophilic attack and the possibility of autocatalytic processing.",
                        notes="Brannigan et al. 1995 establish that the Ntn-hydrolase fold directs autocatalytic processing to generate the mature N-terminal nucleophile chain.",
                    ),
                    CausalEdgeSpec(
                        subject="SO:0000419",
                        predicate="RO:0002331",
                        predicate_label="involved in",
                        object="GO:0051604",
                        description="Formation of the autocatalytically cleaved mature chain completes zymogen protein maturation.",
                        reference="PMID:7477383",
                        evidence_code="ECO:0000269",
                        snippet="This fold provides both the capacity for nucleophilic attack and the possibility of autocatalytic processing.",
                        notes="Self-activation via autocatalytic processing matures the amidohydrolase precursor.",
                    ),
                    CausalEdgeSpec(
                        subject="SO:0000419",
                        predicate="RO:0002327",
                        predicate_label="enables",
                        object="GO:0003824",
                        description="The newly exposed N-terminal Cys, Ser, or Thr residue of the mature polypeptide chain acts as the catalytic nucleophile.",
                        reference="PMID:7477383",
                        evidence_code="ECO:0000269",
                        snippet="These enzymes use the side chain of the amino-terminal residue, incorporated in a beta-sheet, as the nucleophile in the catalytic attack at the carbonyl carbon.",
                        notes="The amino-terminal residue liberated by autocatalytic processing directly catalyzes nucleophilic attack at the substrate carbonyl carbon.",
                    ),
                ),
            ),
        ),
    ),
    TraitSpec(
        rel_dir="structure/allosteric_site",
        filename="covalent-allosteric-regulatory-site.yaml",
        identifier="proteintraitsmech:ALLOSTERIC_COVALENT_REGULATORY_SITE",
        label="covalent allosteric regulatory site",
        definition=(
            "An allosteric regulatory pocket containing a solvent-accessible or cryptically "
            "exposed nucleophilic residue (most commonly a reactive cysteine sulfhydryl, or "
            "lysine/tyrosine side chain) at which covalent adduct formation by an endogenous "
            "electrophile, reactive metabolite, or targeted covalent allosteric modulator "
            "allosterically shifts the protein conformational ensemble and regulates "
            "orthosteric ligand affinity, catalysis, or effector binding."
        ),
        trait_axis="STRUCTURE",
        trait_category="STRUCT_ALLOSTERIC_SITE",
        parent_traits=("proteintraitsmech:ALLOSTERIC_REGULATORY_SITE",),
        synonyms=(
            ("targeted covalent allosteric pocket", "EXACT_SYNONYM"),
            ("cysteine-reactive allosteric site", "NARROW_SYNONYM"),
            ("electrophile-modified allosteric regulatory site", "RELATED_SYNONYM"),
        ),
        evidence=(
            (
                "PMID:24256730",
                "Small molecules that irreversibly bind to a reactive cysteine in the K-Ras(G12C) switch-II allosteric pocket subvert nucleotide preference and impair effector interactions.",
            ),
        ),
        detection_methods=(M_FPOCKET,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="covalent_allosteric_cysteine_adduct_regulation",
                label="Covalent effector modification of a nucleophilic residue in an allosteric pocket shifts the conformational ensemble to regulate protein activity",
                mechanism_summary=(
                    "An electrophilic allosteric effector binds within a topographically distinct "
                    "allosteric pocket and forms a covalent bond with a nucleophilic cysteine side "
                    "chain, remodeling surrounding switch loops to allosterically regulate nucleotide "
                    "affinity and downstream effector or enzymatic activity."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="CHEBI:35224",
                        label="effector",
                        node_type="LIGAND",
                        grounding="CHEBI:35224",
                        description="Electrophilic small-molecule allosteric modulator that covalently modifies the allosteric pocket.",
                    ),
                    CausalNodeSpec(
                        node_id="CHEBI:29950",
                        label="L-cysteine residue",
                        node_type="RESIDUE",
                        grounding="CHEBI:29950",
                        description="Nucleophilic cysteine residue positioned within the allosteric pocket that anchors covalent ligand binding.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0036094",
                        label="small molecule binding",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0036094",
                        description="Covalent capture and pocket occupancy of the small-molecule effector within the allosteric site.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0030234",
                        label="enzyme regulator activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0030234",
                        description="Allosteric regulation of nucleotide/substrate preference and downstream effector interaction.",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="GO:0036094",
                        predicate="RO:0002233",
                        predicate_label="has input",
                        object="CHEBI:35224",
                        description="Allosteric pocket capture takes the covalent small-molecule effector as input.",
                        reference="PMID:24256730",
                        evidence_code="ECO:0000269",
                        snippet="Here we report the development of small molecules that irreversibly bind to a common oncogenic mutant, K-Ras(G12C).",
                        notes="Ostrem et al. 2013 demonstrate irreversible small-molecule binding to the switch-II allosteric pocket of K-Ras(G12C).",
                    ),
                    CausalEdgeSpec(
                        subject="CHEBI:29950",
                        predicate="RO:0000056",
                        predicate_label="participates in",
                        object="GO:0036094",
                        description="The nucleophilic L-cysteine residue in the allosteric pocket forms the covalent bond that anchors small-molecule binding.",
                        reference="PMID:24256730",
                        evidence_code="ECO:0000269",
                        snippet="These compounds rely on the mutant cysteine for binding and therefore do not affect the wild-type protein.",
                        notes="Covalent tethering or electrophilic reaction at the pocket cysteine residue is required for allosteric modulator binding.",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0036094",
                        predicate="RO:0002411",
                        predicate_label="causally upstream of",
                        object="GO:0030234",
                        description="Covalent occupancy of the allosteric pocket remodels switch-I and switch-II conformations to regulate nucleotide preference and effector binding.",
                        reference="PMID:24256730",
                        evidence_code="ECO:0000269",
                        snippet="Binding of these inhibitors to K-Ras(G12C) disrupts both switch-I and switch-II, subverting the native nucleotide preference to favour GDP over GTP and impairing binding to Raf.",
                        notes="Covalent binding in the switch-II pocket allosterically controls nucleotide affinity and effector interactions.",
                    ),
                ),
            ),
        ),
    ),
    TraitSpec(
        rel_dir="structure/disulfide",
        filename="catalytic-cxxc-dithiol-disulfide-active-site-motif.yaml",
        identifier="proteintraitsmech:DISULFIDE_CATALYTIC_CXXC",
        label="catalytic CXXC dithiol-disulfide active-site motif",
        definition=(
            "A redox-active catalytic disulfide/dithiol motif (canonical consensus C-X-X-C, "
            "such as CGPC in thioredoxin, CPYC in glutaredoxin, CGHC in protein disulfide "
            "isomerase, and CPHC in DsbA) positioned at the N-terminus of an alpha-helix in "
            "thioredoxin-fold oxidoreductases, where the solvent-exposed N-terminal cysteine "
            "has a depressed pKa and initiates nucleophilic dithiol-disulfide exchange on "
            "substrate proteins while the buried C-terminal resolving cysteine completes "
            "intramolecular disulfide formation or substrate reduction."
        ),
        trait_axis="STRUCTURE",
        trait_category="STRUCT_DISULFIDE",
        parent_traits=("proteintraitsmech:DISULFIDE_ALLOSTERIC_REDOX_SWITCH",),
        synonyms=(
            ("thioredoxin-fold CXXC catalytic disulfide", "NARROW_SYNONYM"),
            ("redox-active CXXC dithiol/disulfide couple", "EXACT_SYNONYM"),
            ("attacking and resolving cysteine CXXC motif", "RELATED_SYNONYM"),
        ),
        sequence_pattern="C[A-Z]{2}C",
        evidence=(
            (
                "PMID:9403310",
                "Thiol:disulfide oxidoreductases contain a catalytic CXXC motif in which the low-pKa thiolate of the N-terminal cysteine initiates substrate disulfide reduction via nucleophilic attack.",
            ),
        ),
        detection_methods=(M_DSSP_SSBOND,),
        causal_graphs=(
            CausalGraphSpec(
                graph_id="catalytic_cxxc_dithiol_disulfide_exchange",
                label="Nucleophilic attack by the N-terminal CXXC thiolate and resolution by the C-terminal cysteine catalyze thiol-disulfide oxidoreduction",
                mechanism_summary=(
                    "In thiol:disulfide oxidoreductases, the low-pKa thiolate of the N-terminal "
                    "cysteine in the active-site CXXC motif performs a nucleophilic attack on a "
                    "substrate disulfide bond to form a mixed-disulfide intermediate, which is "
                    "resolved by the C-terminal CXXC cysteine to yield an intramolecular CXXC "
                    "cystine cross-link and maintain cellular redox homeostasis."
                ),
                nodes=(
                    CausalNodeSpec(
                        node_id="CHEBI:29950",
                        label="L-cysteine residue",
                        node_type="RESIDUE",
                        grounding="CHEBI:29950",
                        description="Nucleophilic N-terminal L-cysteine thiolate and resolving C-terminal L-cysteine of the catalytic CXXC motif.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0015035",
                        label="protein-disulfide reductase activity",
                        node_type="MOLECULAR_FUNCTION",
                        grounding="GO:0015035",
                        description="Catalytic dithiol-disulfide exchange that reduces target protein disulfide bonds.",
                    ),
                    CausalNodeSpec(
                        node_id="MOD:00034",
                        label="L-cystine (cross-link)",
                        node_type="PTM",
                        grounding="MOD:00034",
                        description="Reversible intramolecular disulfide bond formed between the attacking and resolving cysteines of the CXXC motif.",
                    ),
                    CausalNodeSpec(
                        node_id="GO:0045454",
                        label="cell redox homeostasis",
                        node_type="BIOLOGICAL_PROCESS",
                        grounding="GO:0045454",
                        description="Cellular thiol-disulfide redox balance maintained by thioredoxin-fold CXXC oxidoreductases.",
                    ),
                ),
                edges=(
                    CausalEdgeSpec(
                        subject="CHEBI:29950",
                        predicate="RO:0000056",
                        predicate_label="participates in",
                        object="GO:0015035",
                        description="The thiolate form of the N-terminal cysteine residue in the CXXC motif performs the nucleophilic attack that initiates substrate disulfide reduction.",
                        reference="PMID:9403310",
                        evidence_code="ECO:0000269",
                        snippet="To initiate the reduction of a substrate disulfide bond, the thiolate form of the N-terminal cysteine residue (CXXC) of this motif performs a nucleophilic attack.",
                        notes="Chivers et al. 1997 establish the microscopic pKa and nucleophilic role of the N-terminal Cys32 in the E. coli thioredoxin CXXC motif.",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0015035",
                        predicate="RO:0002234",
                        predicate_label="has output",
                        object="MOD:00034",
                        description="Resolution of the mixed-disulfide intermediate by the C-terminal CXXC cysteine releases the reduced substrate and yields an oxidized CXXC cystine cross-link.",
                        reference="PMID:9403310",
                        evidence_code="ECO:0000269",
                        snippet="Thiol:disulfide oxidoreductases have a CXXC motif within their active sites.",
                        notes="Dithiol-disulfide exchange cycles the active-site CXXC motif between dithiol and intramolecular cystine disulfide states.",
                    ),
                    CausalEdgeSpec(
                        subject="GO:0015035",
                        predicate="RO:0002331",
                        predicate_label="involved in",
                        object="GO:0045454",
                        description="CXXC-catalyzed protein-disulfide reduction maintains cellular thiol-disulfide redox homeostasis.",
                        reference="PMID:9403310",
                        evidence_code="ECO:0000269",
                        snippet="Escherichia coli thioredoxin [Trx (CGPC)] is the best characterized thiol:disulfide oxidoreductase.",
                        notes="Thioredoxin CGPC oxidoreductase activity is a primary effector of cellular dithiol-disulfide redox homeostasis.",
                    ),
                ),
            ),
        ),
    ),
    TraitSpec(
        rel_dir="structure/surface",
        filename="surface-electrostatic-patch.yaml",
        identifier="proteintraitsmech:SURFACE_ELECTROSTATIC_PATCH",
        label="solvent-accessible electrostatic surface patch",
        definition=(
            "A contiguous region on a protein's solvent-accessible molecular surface "
            "exhibiting a pronounced positive or negative electrostatic potential (typically "
            "|phi| >= 1 to 2 kT/e as computed by Poisson-Boltzmann continuum electrostatics "
            "over clustered ionizable side chains and polar backbone atoms), governing "
            "long-range electrostatic steering, macromolecular partner recognition, pH-dependent "
            "stability, and diffusional encounter rates."
        ),
        trait_axis="STRUCTURE",
        trait_category="STRUCT_SURFACE",
        parent_traits=("PATO:0002193",),
        synonyms=(
            ("electrostatic potential surface patch", "EXACT_SYNONYM"),
            ("charged solvent-accessible surface cluster", "RELATED_SYNONYM"),
        ),
        evidence=(
            (
                "PMID:7761829",
                "Numerical solution of the Poisson-Boltzmann equation maps electrostatic potentials across protein solvent-accessible surfaces that govern macromolecular recognition and electrostatic steering.",
            ),
            (
                "PMID:11517324",
                "Continuum electrostatic calculations with APBS characterize biomolecular surface electrostatic potential patches across proteins and supramolecular assemblies.",
            ),
        ),
        detection_methods=(M_FREESASA,),
    ),
    TraitSpec(
        rel_dir="structure/surface",
        filename="positively-charged-cationic-surface-patch.yaml",
        identifier="proteintraitsmech:SURFACE_BASIC_CATIONIC_PATCH",
        label="positively charged cationic surface patch",
        definition=(
            "A solvent-accessible electrostatic surface patch with a strong net positive "
            "electrostatic potential formed by spatially clustered basic side chains (arginine, "
            "lysine, and protonated histidine) in 3D structure even when non-contiguous in "
            "primary sequence, mediating electrostatic recognition of polyanionic partners "
            "such as duplex DNA, RNA, heparin/heparan sulfate glycosaminoglycans, and "
            "anionic phospholipid headgroups (PIP2, phosphatidylserine, cardiolipin)."
        ),
        trait_axis="STRUCTURE",
        trait_category="STRUCT_SURFACE",
        parent_traits=("proteintraitsmech:SURFACE_ELECTROSTATIC_PATCH", "PATO:0002195"),
        synonyms=(
            ("basic electrostatic surface patch", "EXACT_SYNONYM"),
            ("cationic Arg/Lys surface patch", "RELATED_SYNONYM"),
            ("polyanion-binding positive surface patch", "RELATED_SYNONYM"),
        ),
        evidence=(
            (
                "PMID:14654279",
                "DNA-binding and polyanion-binding sites on protein structures coincide with solvent-accessible surface patches exhibiting the largest positive electrostatic potential scores.",
            ),
        ),
        detection_methods=(M_FREESASA,),
    ),
    TraitSpec(
        rel_dir="structure/surface",
        filename="negatively-charged-acidic-surface-patch.yaml",
        identifier="proteintraitsmech:SURFACE_ACIDIC_ANIONIC_PATCH",
        label="negatively charged acidic surface patch",
        definition=(
            "A solvent-accessible electrostatic surface patch with a strong net negative "
            "electrostatic potential formed by spatially clustered acidic carboxylate side "
            "chains (aspartate and glutamate) on the 3D molecular surface, mediating "
            "long-range electrostatic steering of cationic protein partners (such as "
            "barnase-barstar or cytochrome c complexes), nucleic-acid mimicry, divalent "
            "cation recruitment, or halophilic hydration-shell stabilization."
        ),
        trait_axis="STRUCTURE",
        trait_category="STRUCT_SURFACE",
        parent_traits=("proteintraitsmech:SURFACE_ELECTROSTATIC_PATCH", "PATO:0002196"),
        synonyms=(
            ("acidic electrostatic surface patch", "EXACT_SYNONYM"),
            ("anionic Asp/Glu surface patch", "RELATED_SYNONYM"),
        ),
        evidence=(
            (
                "PMID:8638017",
                "Clustered negatively charged acidic surface residues generate long-range electrostatic steering potentials that accelerate macromolecular association and enhance aqueous solvation.",
            ),
            (
                "PMID:7761829",
                "Poisson-Boltzmann surface electrostatic potential calculations resolve anionic surface patches on proteins.",
            ),
        ),
        detection_methods=(M_FREESASA,),
    ),
    TraitSpec(
        rel_dir="structure/surface",
        filename="solvent-exposed-hydrophobic-surface-patch.yaml",
        identifier="proteintraitsmech:SURFACE_HYDROPHOBIC_PATCH",
        label="solvent-exposed hydrophobic surface patch",
        definition=(
            "A contiguous cluster of solvent-accessible nonpolar side chains (Leu, Ile, Val, "
            "Phe, Trp, Met, Tyr, Ala) exposed on the exterior surface of a folded protein "
            "domain (quantified by spatial aggregation propensity SAP or structure-corrected "
            "CamSol hydrophobicity), providing the thermodynamic desolvation driving force "
            "for high-affinity protein-protein interaction hot spots, peripheral membrane "
            "association, or concentration-dependent self-association and aggregation."
        ),
        trait_axis="STRUCTURE",
        trait_category="STRUCT_SURFACE",
        parent_traits=("PATO:0001884",),
        synonyms=(
            ("nonpolar solvent-accessible surface patch", "EXACT_SYNONYM"),
            ("spatial aggregation propensity (SAP) hydrophobic patch", "RELATED_SYNONYM"),
        ),
        evidence=(
            (
                "PMID:19571001",
                "Spatial aggregation propensity (SAP) identifies dynamically exposed hydrophobic surface patches on folded proteins that mediate protein-protein interaction and self-association.",
            ),
            (
                "PMID:25451785",
                "CamSol profiles solvent-exposed hydrophobic and polar surface patches to quantify native-state protein solubility.",
            ),
        ),
        detection_methods=(M_FREESASA,),
    ),
    TraitSpec(
        rel_dir="structure/surface",
        filename="surface-glycan-steric-shield.yaml",
        identifier="proteintraitsmech:SURFACE_GLYCOSYLATION_SHIELD",
        label="surface glycan steric shield",
        definition=(
            "A dense array of covalently attached N-linked or O-linked oligosaccharide "
            "chains distributed across a protein's solvent-accessible surface whose "
            "conformational ensembles collectively occlude underlying polypeptide surface "
            "area from macromolecular probes, shielding viral envelope glycoproteins and "
            "secreted cell-surface proteins from neutralizing antibodies and host proteases."
        ),
        trait_axis="STRUCTURE",
        trait_category="STRUCT_SURFACE",
        synonyms=(
            ("glycan shield", "EXACT_SYNONYM"),
            ("N-glycan surface steric canopy", "RELATED_SYNONYM"),
        ),
        evidence=(
            (
                "PMID:12646921",
                "Dense N-linked glycosylation across the solvent-accessible surface of viral envelope glycoproteins forms an evolving glycan shield that sterically occludes underlying neutralizing epitopes.",
            ),
        ),
        detection_methods=(M_FREESASA,),
    ),
    TraitSpec(
        rel_dir="structure/surface",
        filename="interfacial-aromatic-tryptophan-tyrosine-membrane-belt.yaml",
        identifier="proteintraitsmech:SURFACE_MEMBRANE_ANCHORING_AROMATIC_BELT",
        label="interfacial aromatic tryptophan/tyrosine membrane belt",
        definition=(
            "A ring-like surface arrangement of solvent- and lipid-exposed tryptophan and "
            "tyrosine side chains flanking the hydrophobic transmembrane barrel or alpha-helical "
            "bundle of an integral membrane protein at the membrane-water interface (~12 to 15 A "
            "from the bilayer midplane), anchoring vertical orientation and matching bilayer "
            "thickness via dipolar, quadrupolar, and hydrogen-bonding interactions with lipid "
            "glycerol/carbonyl headgroups."
        ),
        trait_axis="STRUCTURE",
        trait_category="STRUCT_SURFACE",
        synonyms=(
            ("membrane-water interfacial aromatic girdle", "EXACT_SYNONYM"),
            ("Trp/Tyr transmembrane flanking aromatic ring belt", "RELATED_SYNONYM"),
        ),
        evidence=(
            (
                "PMID:9778346",
                "Transmembrane alpha-helical bundles and beta-barrels display a conserved surface belt of tryptophan and tyrosine residues positioned at the lipid-water carbonyl/glycerol interface that anchors vertical membrane orientation.",
            ),
        ),
        detection_methods=(M_FREESASA,),
    ),
    TraitSpec(
        rel_dir="structure/dynamics",
        filename="interdomain-hinge-bending-region.yaml",
        identifier="proteintraitsmech:DYNAMICS_DOMAIN_HINGE",
        label="interdomain hinge-bending region",
        definition=(
            "A short flexible polypeptide segment or pair of beta-strands/alpha-helical "
            "joints connecting two quasi-rigid tertiary domains where localized main-chain "
            "torsion-angle rotations (phi/psi changes) drive large-amplitude rigid-body "
            "hinge-bending domain closure and opening (as in periplasmic binding proteins, "
            "adenylate kinase, lactoferrin, and immunoglobulins)."
        ),
        trait_axis="STRUCTURE",
        trait_category="STRUCT_DYNAMICS",
        parent_traits=("proteintraitsmech:ELBOW", "PATO:0001543"),
        synonyms=(
            ("domain hinge axis linker", "EXACT_SYNONYM"),
            ("hinge-bending interdomain pivot", "RELATED_SYNONYM"),
        ),
        evidence=(
            (
                "PMID:8204609",
                "Large-scale rigid-body domain movements in proteins are mediated by localized backbone dihedral rotations within flexible interdomain hinge regions where packing constraints are minimal.",
            ),
        ),
        detection_methods=(M_PRODY_ANM,),
    ),
    TraitSpec(
        rel_dir="structure/dynamics",
        filename="active-site-catalytic-gating-lid-loop.yaml",
        identifier="proteintraitsmech:DYNAMICS_CATALYTIC_GATING_LOOP",
        label="active-site catalytic gating/lid loop",
        definition=(
            "A conformationally mobile surface loop flanking an enzyme active site or "
            "substrate binding pocket that undergoes reversible open-to-closed transitions "
            "(microsecond-to-millisecond timescale) upon ligand binding, desolvating the "
            "catalytic pocket, positioning catalytic residues, and preventing premature "
            "hydrolysis or escape of reactive reaction intermediates (exemplified by "
            "triosephosphate isomerase loop 6, dihydrofolate reductase Met20 loop, and "
            "lipase interfacial lids)."
        ),
        trait_axis="STRUCTURE",
        trait_category="STRUCT_DYNAMICS",
        parent_traits=("PATO:0001543",),
        synonyms=(
            ("catalytic omega-loop lid", "NARROW_SYNONYM"),
            ("substrate-gated active-site closure loop", "EXACT_SYNONYM"),
        ),
        evidence=(
            (
                "PMID:30703322",
                "Substrate binding drives conformational closure of flexible active-site gating loops (such as the triosephosphate isomerase loop 6), sequestering the reaction intermediate from bulk water and stabilizing the catalytic transition state.",
            ),
        ),
        detection_methods=(M_PRODY_ANM,),
    ),
    TraitSpec(
        rel_dir="structure/dynamics",
        filename="metamorphic-fold-switching-region.yaml",
        identifier="proteintraitsmech:DYNAMICS_METAMORPHIC_FOLD_SWITCH",
        label="metamorphic fold-switching region",
        definition=(
            "A polypeptide region or domain capable of reversible, large-scale remodeling "
            "of its secondary and tertiary structure (such as alpha-helix to beta-sheet "
            "interconversion) between two or more distinct, stable native fold topologies "
            "under physiological conditions (exemplified by RfaH C-terminal domain, XCL1 "
            "lymphotactin, KaiB, and Mad2), exposing distinct functional surfaces in each fold state."
        ),
        trait_axis="STRUCTURE",
        trait_category="STRUCT_DYNAMICS",
        parent_traits=("PATO:0001543",),
        synonyms=(
            ("fold-switching metamorphic protein segment", "EXACT_SYNONYM"),
            ("reversible secondary- and tertiary-structure remodeling region", "RELATED_SYNONYM"),
        ),
        evidence=(
            (
                "PMID:18583598",
                "Metamorphic proteins reversibly interconvert between two distinct, stable native fold topologies with different secondary-structure elements and biological functions under physiological conditions.",
            ),
            (
                "PMID:20591649",
                "Fold-switching proteins remodel secondary and tertiary structure across flexible regions to expose alternative binding surfaces and expand biological function.",
            ),
        ),
        detection_methods=(M_PRODY_ANM,),
    ),
    TraitSpec(
        rel_dir="structure/dynamics",
        filename="3d-domain-swapping-hinge-loop.yaml",
        identifier="proteintraitsmech:DYNAMICS_DOMAIN_SWAPPING_HINGE_LOOP",
        label="3D domain-swapping hinge loop",
        definition=(
            "A conformationally bistable polypeptide loop that folds back on its own chain "
            "in the closed monomeric state but adopts an extended conformation in the "
            "3D domain-swapped state, allowing an adjacent secondary-structure element or "
            "tertiary domain to exchange into the equivalent position of an identical partner "
            "subunit to form an intertwined dimer or higher oligomer."
        ),
        trait_axis="STRUCTURE",
        trait_category="STRUCT_DYNAMICS",
        parent_traits=("proteintraitsmech:ELBOW", "PATO:0001543"),
        synonyms=(
            ("three-dimensional domain-swapping hinge segment", "EXACT_SYNONYM"),
            ("monomer-to-swapped-oligomer hinge loop", "RELATED_SYNONYM"),
        ),
        evidence=(
            (
                "PMID:8580836",
                "In 3D domain swapping, conformational extension of a flexible hinge loop allows a secondary or tertiary structural segment of one monomeric chain to exchange with the identical segment of an adjacent subunit, forming an intertwined dimer or higher oligomer.",
            ),
        ),
        detection_methods=(M_PRODY_ANM, M_PISA),
    ),
    TraitSpec(
        rel_dir="structure/dynamics",
        filename="allosteric-dynamic-coupling-residue-network.yaml",
        identifier="proteintraitsmech:DYNAMICS_ALLOSTERIC_ENSEMBLE_TRANSMISSION_PATHWAY",
        label="allosteric dynamic-coupling residue network",
        definition=(
            "A contiguous network of dynamically coupled residues spanning the tertiary "
            "interior between a distal allosteric site and an orthosteric catalytic or "
            "binding site, through which correlated side-chain rotamer and backbone "
            "fluctuations propagate allosteric free-energy perturbations across community "
            "interfaces, including entropically driven allostery without large mean-backbone "
            "displacement."
        ),
        trait_axis="STRUCTURE",
        trait_category="STRUCT_DYNAMICS",
        parent_traits=("PATO:0001543",),
        synonyms=(
            ("allosteric conformational communication pathway", "EXACT_SYNONYM"),
            ("correlated-motion residue community network", "RELATED_SYNONYM"),
        ),
        evidence=(
            (
                "PMID:19351898",
                "Correlated residue fluctuations in protein dynamical networks form interconnected communities and critical inter-community edges that transmit allosteric signals between distant effector and catalytic sites.",
            ),
        ),
        detection_methods=(M_PRODY_ANM,),
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
    if spec.evolutionary_scope:
        lines.append("evolutionary_scope:")
        for k, v in spec.evolutionary_scope:
            if isinstance(v, (int, float)):
                lines.append(f"  {k}: {v}")
            else:
                lines.append(f"  {k}: {yaml_escape(str(v))}")
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
            write_record(path, emit_record(spec), validate=True)
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

    n_cats = len({s.trait_category for s in SPECS})
    print(f"{len(SPECS)} foundational protein-trait records defined across {n_cats} categories.")
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
