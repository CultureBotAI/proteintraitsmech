#!/usr/bin/env python3
"""Seed ProteinTraitRecord YAMLs under data/traits/structure/ from the
LinkML valuesets `LocalStructuralFeature` enumeration.

Source:
  https://linkml.io/valuesets/elements/LocalStructuralFeature/

Behaviour:
  - Default: dry-run — print per-term action and per-category counts.
  - --apply: write YAMLs.
  - --force: overwrite existing YAMLs when applying (default preserves them).

Stdlib-only (no PyYAML dep) — YAML is templated as text so a fresh checkout
can seed before `just install`.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from record_io import write_record  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data" / "traits" / "structure"

SOURCE_ENUM = "valuesets:LocalStructuralFeature"
SOURCE_URL = "https://linkml.io/valuesets/elements/LocalStructuralFeature/"
DEFINITION_SOURCE = SOURCE_URL

PARENT_MOTIF = "proteintraitsmech:POLYPEPTIDE_STRUCTURAL_MOTIF"

# Terms which are conceptually sub-motifs of POLYPEPTIDE_STRUCTURAL_MOTIF —
# small, recurring 3D structural elements that don't form a globular unit.
CHILD_MOTIFS = {
    "BETA_HAIRPIN",
    "BETA_BULGE",
    "ASX_MOTIF",
    "NEST",
    "COILED_COIL",
    "HELIX_CAP",
    "KINK",
    "ELBOW",
}

# One entry per permissible value on the source enum.
# subdir is the directory under data/traits/structure/ (kept short by dropping
# the redundant STRUCT_ prefix from the category enum value).
TERMS = [
    {
        "term": "POLYPEPTIDE_STRUCTURAL_MOTIF",
        "label": "polypeptide structural motif",
        "definition": "A recurring 3D structural element within the chain that does not form a stable globular unit.",
        "category": "STRUCT_SECONDARY",
        "subdir": "secondary",
        "so_xref": "SO:0001079",
    },
    {
        "term": "BETA_HAIRPIN",
        "label": "beta hairpin",
        "definition": "Two adjacent antiparallel beta strands connected by a short loop or turn.",
        "category": "STRUCT_SECONDARY",
        "subdir": "secondary",
        "so_xref": None,
    },
    {
        "term": "BETA_BULGE",
        "label": "beta bulge",
        "definition": "A local disruption of beta-sheet hydrogen bonding across three residues.",
        "category": "STRUCT_SECONDARY",
        "subdir": "secondary",
        "so_xref": "SO:0001107",
    },
    {
        "term": "ASX_MOTIF",
        "label": "asx motif",
        "definition": "A five-residue motif nucleated by an Asp/Asn side chain (Asx).",
        "category": "STRUCT_SECONDARY",
        "subdir": "secondary",
        "so_xref": "SO:0001106",
    },
    {
        "term": "NEST",
        "label": "nest",
        "definition": "A motif of two consecutive residues forming an anion-binding concavity.",
        "category": "STRUCT_SECONDARY",
        "subdir": "secondary",
        "so_xref": "SO:0001120",
    },
    {
        "term": "COILED_COIL",
        "label": "coiled coil",
        "definition": "Two or more alpha helices wound together like strands of a rope.",
        "category": "STRUCT_SECONDARY",
        "subdir": "secondary",
        "so_xref": "SO:0001080",
    },
    {
        "term": "HELIX_CAP",
        "label": "helix cap",
        "definition": "N-cap or C-cap residue terminating an alpha helix.",
        "category": "STRUCT_SECONDARY",
        "subdir": "secondary",
        "so_xref": None,
    },
    {
        "term": "KINK",
        "label": "kink",
        "definition": "A localized bend interrupting the regular geometry of a helix.",
        "category": "STRUCT_SECONDARY",
        "subdir": "secondary",
        "so_xref": None,
    },
    {
        "term": "CATALYTIC_RESIDUE",
        "label": "catalytic residue",
        "definition": (
            "An amino acid residue within an enzyme active site that participates directly in "
            "the chemical mechanism of catalysis — acting as a nucleophile, general acid/base "
            "proton donor or acceptor, covalent intermediate carrier, transition-state or "
            "intermediate stabilizer, or direct activator of a catalytic water or cofactor."
        ),
        "category": "STRUCT_ACTIVE_SITE",
        "subdir": "active_site",
        "so_xref": "SO:0001104",
        "extra_blocks": """causal_graphs:
- graph_id: CG_CATALYTIC_RESIDUE
  title: Active-site catalytic residues drive substrate activation and enzymatic turnover
  description: Catalytic amino-acid residues (CHEBI:83228) within an enzyme active site orient and activate
    bound small-molecule substrates or cofactors (GO:0036094), directly enabling enzymatic catalytic activity
    (GO:0003824) that drives cellular metabolic processes (GO:0008152).
  nodes:
  - node_id: CHEBI:83228
    label: amino-acid residue
    node_type: RESIDUE
    grounding: CHEBI:83228
    description: Active-site amino-acid residue acting as nucleophile, general acid/base, or transition-state
      stabilizer
  - node_id: GO:0036094
    label: small molecule binding
    node_type: MOLECULAR_FUNCTION
    grounding: GO:0036094
    description: Productive positioning and polarization of substrates, cofactors, and reaction intermediates
      in the active-site environment
  - node_id: GO:0003824
    label: catalytic activity
    node_type: MOLECULAR_FUNCTION
    grounding: GO:0003824
    description: Direct chemical catalysis of bond cleavage, bond formation, or group transfer by active-site
      residues
  - node_id: GO:0008152
    label: metabolic process
    node_type: BIOLOGICAL_PROCESS
    grounding: GO:0008152
    description: Cellular biochemical reaction pathways driven by enzymatic catalysis
  edges:
  - subject: CHEBI:83228
    predicate: enables
    predicate_id: RO:0002327
    object: GO:0036094
    description: Conserved active-site amino acid residues establish the electrostatic and steric active-site
      environment that binds and polarizes substrates and cofactors.
    evidence:
    - reference: PMID:12421562
      snippet: The results indicate the dominance of a small set of amino acid residues in catalysis and
        give a picture of a general active site environment.
      notes: Active-site amino acid residues establish the catalytic environment (PMID:12421562) (ECO:0000269)
  - subject: GO:0036094
    predicate: causally upstream of
    predicate_id: RO:0002411
    object: GO:0003824
    description: Substrate and cofactor engagement by catalytic residues in the active site directly drives
      enzymatic chemical catalysis.
    evidence:
    - reference: PMID:12421562
      snippet: We present an analysis of the residues directly involved in catalysis in 178 enzyme active
        sites. Specific criteria were derived to define a catalytic residue, and used to create a catalytic
        residue dataset, which was then analysed in terms of properties including secondary structure,
        solvent accessibility, flexibility, conservation, quaternary structure and function.
      notes: Catalytic residues directly execute enzyme active-site catalysis (PMID:12421562) (ECO:0000269)
  - subject: GO:0003824
    predicate: positively regulates
    predicate_id: RO:0002213
    object: GO:0008152
    description: Enzyme reaction mechanisms mediated by catalytic sites drive biological metabolic transformations.
    evidence:
    - reference: PMID:29106569
      snippet: M-CSA (Mechanism and Catalytic Site Atlas) is a database of enzyme active sites and reaction
        mechanisms that can be accessed at www.ebi.ac.uk/thornton-srv/m-csa. Our objectives with M-CSA
        are to provide an open data resource for the community to browse known enzyme reaction mechanisms
        and catalytic sites, and to use the dataset to understand enzyme function and evolution.
      notes: Catalytic sites and reaction mechanisms drive enzyme function (PMID:29106569) (ECO:0000305)
evidence:
- reference: PMID:12421562
  notes: Bartlett et al. (2002) define the criteria and functional roles of amino acid residues directly
    involved in catalysis across 178 enzyme active sites.
- reference: PMID:29106569
  notes: Ribeiro et al. (2018) describe the Mechanism and Catalytic Site Atlas (M-CSA) cataloguing catalytic
    residues and enzyme reaction mechanisms.""",
    },
    {
        "term": "PROTEIN_BINDING_SITE",
        "label": "protein binding site",
        "definition": (
            "A contiguous or discontinuous structural patch of amino acid residues on a protein "
            "surface or domain that interacts selectively and non-covalently with a polypeptide "
            "or protein partner via shape complementarity, hydrogen bonds, salt bridges, and "
            "buried hydrophobic contacts to mediate protein-protein recognition and complex assembly."
        ),
        "category": "STRUCT_BINDING_SITE",
        "subdir": "binding_site",
        "so_xref": "SO:0000410",
        "extra_xrefs": ["SO:0001091"],
        "extra_blocks": """causal_graphs:
- graph_id: CG_PROTEIN_BINDING_SITE
  title: Surface binding-site residues mediate selective protein binding and complex assembly
  description: Contact amino-acid residues (CHEBI:83228) within a protein binding site form complementary
    non-covalent interactions that enable selective protein binding (GO:0005515), positively regulating
    protein complex oligomerization (GO:0051259) to assemble a stable protein-containing complex (GO:0032991).
  nodes:
  - node_id: CHEBI:83228
    label: amino-acid residue
    node_type: RESIDUE
    grounding: CHEBI:83228
    description: Surface-exposed binding-site amino-acid residues forming non-covalent contacts with a
      polypeptide partner
  - node_id: GO:0005515
    label: protein binding
    node_type: MOLECULAR_FUNCTION
    grounding: GO:0005515
    description: Selective non-covalent recognition of a partner domain or linear peptide motif
  - node_id: GO:0051259
    label: protein complex oligomerization
    node_type: BIOLOGICAL_PROCESS
    grounding: GO:0051259
    description: Assembly of interacting polypeptide chains into a multiprotein oligomer or complex
  - node_id: GO:0032991
    label: protein-containing complex
    node_type: CELLULAR_LOCALIZATION
    grounding: GO:0032991
    description: Stable or transient macromolecular complex formed by interacting protein subunits
  edges:
  - subject: CHEBI:83228
    predicate: enables
    predicate_id: RO:0002327
    object: GO:0005515
    description: Clustered interface residues at the binding site define conserved interaction topologies
      that enable selective protein binding.
    evidence:
    - reference: PMID:24081580
      snippet: For every interaction, 3did identifies and groups different binding modes by clustering
        similar interfaces into 'interaction topologies'.
      notes: Binding-site residue contacts define conserved protein-binding modes (PMID:24081580) (ECO:0000305)
  - subject: GO:0005515
    predicate: positively regulates
    predicate_id: RO:0002213
    object: GO:0051259
    description: Selective domain-domain and domain-motif binding drives multiprotein complex assembly
      across protein interaction networks.
    evidence:
    - reference: PMID:24081580
      snippet: By maintaining a constantly updated collection of domain-based structural interaction templates,
        3did is a reference source of information for the structural characterization of protein interaction
        networks.
      notes: Structural protein binding templates mediate protein interaction assembly (PMID:24081580)
        (ECO:0000305)
  - subject: GO:0051259
    predicate: has output
    predicate_id: RO:0002234
    object: GO:0032991
    description: Oligomerization of interacting subunits produces a functional protein-containing complex.
    evidence:
    - reference: PMID:24081580
      snippet: By maintaining a constantly updated collection of domain-based structural interaction templates,
        3did is a reference source of information for the structural characterization of protein interaction
        networks.
      notes: Assembled domain interactions form protein-containing complexes (PMID:24081580) (ECO:0000305)
evidence:
- reference: PMID:24081580
  notes: Mosca et al. (2014) characterize domain-based and motif-based protein-protein binding sites and
    interaction topologies across high-resolution 3D structures in 3did.""",
    },
    {
        "term": "DISULFIDE_BOND",
        "label": "disulfide bond",
        "definition": (
            "A covalent sulfur-sulfur (S-S) cross-link (L-cystine, MOD:00034) formed by oxidative "
            "coupling of the thiol side chains of two cysteine residues (CHEBI:29950) within the "
            "same polypeptide chain (intrachain) or between distinct chains (interchain), "
            "catalyzed by thiol-disulfide oxidoreductases to stabilize tertiary/quaternary "
            "fold or act as a redox-reversible allosteric switch."
        ),
        "category": "STRUCT_DISULFIDE",
        "subdir": "disulfide",
        "so_xref": None,
        "extra_xrefs": ["SO:0001088"],
        "extra_blocks": """causal_graphs:
- graph_id: CG_DISULFIDE_BOND
  title: Thiol-isomerase-catalyzed oxidation of cysteine pairs into structural and allosteric disulfide
    bonds
  description: Paired L-cysteine residues (CHEBI:29950) undergo oxidative thiol-disulfide exchange catalyzed
    by protein disulfide isomerase activity (GO:0003756) to yield a covalent L-cystine disulfide cross-link
    (MOD:00034), which positively regulates oxidative protein folding and structural integrity (GO:0006457).
  nodes:
  - node_id: CHEBI:29950
    label: L-cysteine residue
    node_type: RESIDUE
    grounding: CHEBI:29950
    description: Paired thiol-bearing L-cysteine residues juxtaposed in the nascent or mature polypeptide
      chain
  - node_id: GO:0003756
    label: protein disulfide isomerase activity
    node_type: MOLECULAR_FUNCTION
    grounding: GO:0003756
    description: Thiol-disulfide oxidoreductase activity catalyzing disulfide bond formation and rearrangement
  - node_id: MOD:00034
    label: L-cystine (cross-link)
    node_type: PTM
    grounding: MOD:00034
    description: Covalent S-S disulfide cross-link bridging two cysteine residues
  - node_id: GO:0006457
    label: protein folding
    node_type: BIOLOGICAL_PROCESS
    grounding: GO:0006457
    description: Oxidative protein folding and stabilization of native tertiary/quaternary structural
      integrity
  edges:
  - subject: CHEBI:29950
    predicate: participates in
    predicate_id: RO:0000056
    object: GO:0003756
    description: Reduced cysteine thiol pairs in nascent polypeptides participate as substrates in protein
      disulfide isomerase-catalyzed disulfide oxidation.
    evidence:
    - reference: PMID:19005088
      snippet: We show here that cysteine oxidation is catalyzed strictly by the enzyme Protein Disulfide
        Isomerase (PDI) and not by other members of the PDI family.
      notes: Protein disulfide isomerase catalyzes cysteine oxidation into disulfide bonds (PMID:19005088)
        (ECO:0000269)
  - subject: GO:0003756
    predicate: has output
    predicate_id: RO:0002234
    object: MOD:00034
    description: Protein disulfide isomerase catalysis generates covalent L-cystine (S-S) cross-links.
    evidence:
    - reference: PMID:19005088
      snippet: We show here that cysteine oxidation is catalyzed strictly by the enzyme Protein Disulfide
        Isomerase (PDI) and not by other members of the PDI family.
      notes: PDI-catalyzed cysteine oxidation produces covalent L-cystine disulfide bonds (PMID:19005088)
        (ECO:0000269)
  - subject: MOD:00034
    predicate: positively regulates
    predicate_id: RO:0002213
    object: GO:0006457
    description: Covalent disulfide cross-links stabilize native tertiary and quaternary protein folding
      and can act as redox-regulated allosteric switches.
    evidence:
    - reference: PMID:19005088
      snippet: Our results indicate that individual cysteine residues that remain available for disulfide
        bond formation in the folded monomer can form interchain disulfide bonds with a variety of different
        cysteine residues present in a companion subunit.
      notes: Disulfide cross-links form during monomer folding and subunit assembly (PMID:19005088) (ECO:0000269)
evidence:
- reference: PMID:19005088
  notes: Protein disulfide isomerase (PDI) catalyzes cysteine oxidation and disulfide bond formation during
    oxidative protein folding and subunit assembly.
- reference: PMID:16959969
  notes: Disulfide bonds form structural cross-links and redox-sensitive allosteric switches that regulate
    mature protein function when cleaved or isomerized by oxidoreductases.""",
    },
    {
        "term": "METAL_BINDING_SITE",
        "label": "metal binding site",
        "definition": (
            "A three-dimensional local coordination site (Minimal Functional Site) within a "
            "protein structure in which amino acid side-chain or backbone donor atoms (typically "
            "His, Cys, Asp, or Glu) coordinate one or more metal ions or polynuclear metal "
            "clusters with defined geometry to stabilize protein fold, mediate electron transfer, "
            "or catalyze enzymatic reactions."
        ),
        "category": "STRUCT_METAL_SITE",
        "subdir": "metal_site",
        "so_xref": None,
        "extra_xrefs": ["GO:0046872"],
        "extra_blocks": """causal_graphs:
- graph_id: CG_METAL_BINDING_SITE
  title: Minimal functional metal-binding site coordinates metal cofactors for fold stability and catalysis
  description: First-shell coordinating amino-acid residues (CHEBI:83228) within a metal binding site
    form a Minimal Functional Site that enables selective metal ion binding (GO:0046872), positively regulating
    protein structural stability (GO:0031647) and enabling metalloenzyme catalytic activity (GO:0003824).
  nodes:
  - node_id: CHEBI:83228
    label: amino-acid residue
    node_type: RESIDUE
    grounding: CHEBI:83228
    description: First-sphere donor amino-acid residues (His, Cys, Asp, Glu, and backbone carbonyls) forming
      the local metal coordination environment
  - node_id: GO:0046872
    label: metal ion binding
    node_type: MOLECULAR_FUNCTION
    grounding: GO:0046872
    description: Coordination of one or more metal ions or polynuclear clusters within the Minimal Functional
      Site
  - node_id: GO:0031647
    label: regulation of protein stability
    node_type: BIOLOGICAL_PROCESS
    grounding: GO:0031647
    description: Conformational cross-linking and tertiary fold stabilization imparted by structural metal
      coordination
  - node_id: GO:0003824
    label: catalytic activity
    node_type: MOLECULAR_FUNCTION
    grounding: GO:0003824
    description: Lewis-acid activation, substrate polarization, or redox catalysis mediated by catalytic
      metal centers
  edges:
  - subject: CHEBI:83228
    predicate: enables
    predicate_id: RO:0002327
    object: GO:0046872
    description: Donor amino-acid residues in the local 3D Minimal Functional Site coordinate metal ions
      with defined geometry.
    evidence:
    - reference: PMID:23155064
      snippet: MFSs are 3D templates that describe the local environment around the metal(s) independently
        of the larger context of the macromolecular structure embedding the site(s), and are the central
        objects of MetalPDB design.
      notes: Local 3D residue environment (MFS) coordinates the metal ion(s) (PMID:23155064) (ECO:0000305)
  - subject: GO:0046872
    predicate: positively regulates
    predicate_id: RO:0002213
    object: GO:0031647
    description: Metal coordination within equistructural Minimal Functional Sites stabilizes the local
      and global macromolecular fold.
    evidence:
    - reference: PMID:23155064
      snippet: This is achieved through the systematic and automated representation of metal-binding sites
        in proteins and nucleic acids by way of Minimal Functional Sites (MFSs).
      notes: Minimal Functional Sites organize structural metal coordination in proteins (PMID:23155064)
        (ECO:0000305)
  - subject: GO:0046872
    predicate: enables
    predicate_id: RO:0002327
    object: GO:0003824
    description: Coordinated metal centers in metalloenzyme Minimal Functional Sites directly enable catalytic
      function.
    evidence:
    - reference: PMID:23155064
      snippet: MFSs are grouped into equistructural (broadly defined as sites found in corresponding positions
        in similar structures) and equivalent sites (equistructural sites that contain the same metals),
        allowing users to easily analyse similarities and variations in metal-macromolecule interactions,
        and to link them to functional information.
      notes: Equivalent metal-binding Minimal Functional Sites link metal coordination to catalytic function
        (PMID:23155064) (ECO:0000305)
evidence:
- reference: PMID:23155064
  notes: Andreini et al. (2013) characterize metal-binding Minimal Functional Sites (MFSs) in MetalPDB
    and their structural and catalytic roles in metalloproteins.""",
    },
    {
        "term": "POCKET",
        "label": "pocket",
        "definition": "A concave, solvent-accessible surface depression that can accommodate a ligand.",
        "category": "STRUCT_CAVITY",
        "subdir": "cavity",
        "so_xref": None,
    },
    {
        "term": "CLEFT",
        "label": "cleft",
        "definition": "An elongated surface groove between structural elements or domains.",
        "category": "STRUCT_CAVITY",
        "subdir": "cavity",
        "so_xref": None,
    },
    {
        "term": "CAVITY",
        "label": "cavity",
        "definition": "An enclosed, solvent-inaccessible internal void within the structure.",
        "category": "STRUCT_CAVITY",
        "subdir": "cavity",
        "so_xref": None,
    },
    {
        "term": "TUNNEL",
        "label": "tunnel",
        "definition": "An elongated, often buried, passage through the structure connecting two regions.",
        "category": "STRUCT_CAVITY",
        "subdir": "cavity",
        "so_xref": None,
    },
    {
        "term": "GROOVE",
        "label": "groove",
        "definition": "A surface channel, e.g. a nucleic-acid-binding groove.",
        "category": "STRUCT_CAVITY",
        "subdir": "cavity",
        "so_xref": None,
    },
    {
        "term": "ELBOW",
        "label": "elbow",
        "definition": "A localized bend or hinge between two structural elements or domains.",
        "category": "STRUCT_DYNAMICS",
        "subdir": "dynamics",
        "so_xref": None,
    },
    {
        "term": "INTERFACE",
        "label": "interface",
        "definition": (
            "A solvent-accessible surface patch of interacting residues on a protein subunit or "
            "domain that buries solvent-accessible surface area upon contact with another "
            "polypeptide chain, nucleic acid, or macromolecular partner to drive homomeric or "
            "heteromeric oligomerization and macromolecular complex formation."
        ),
        "category": "STRUCT_INTERFACE",
        "subdir": "interface",
        "so_xref": None,
        "extra_xrefs": ["SO:0001093"],
        "extra_blocks": """causal_graphs:
- graph_id: CG_INTERFACE
  title: Subunit contact interface residues drive dimerization and macromolecular oligomerization
  description: Surface interface residues (CHEBI:83228) bury hydrophobic and polar contact area to enable
    protein binding (GO:0005515), which is causally upstream of subunit dimerization (GO:0046983) and
    positively regulates multiprotein complex oligomerization (GO:0051259).
  nodes:
  - node_id: CHEBI:83228
    label: amino-acid residue
    node_type: RESIDUE
    grounding: CHEBI:83228
    description: Core and rim amino-acid residues on the subunit surface patch that become buried upon
      complex formation
  - node_id: GO:0005515
    label: protein binding
    node_type: MOLECULAR_FUNCTION
    grounding: GO:0005515
    description: Direct non-covalent macromolecular contact across the buried subunit interface
  - node_id: GO:0046983
    label: protein dimerization activity
    node_type: MOLECULAR_FUNCTION
    grounding: GO:0046983
    description: Homodimeric or heterodimeric subunit pairing mediated by conserved interface topologies
  - node_id: GO:0051259
    label: protein complex oligomerization
    node_type: BIOLOGICAL_PROCESS
    grounding: GO:0051259
    description: Assembly of quaternary dimers and higher-order oligomers from interacting subunits
  edges:
  - subject: CHEBI:83228
    predicate: enables
    predicate_id: RO:0002327
    object: GO:0005515
    description: Residue contact patches on the subunit surface cluster into conserved interaction topologies
      that mediate protein binding.
    evidence:
    - reference: PMID:24081580
      snippet: For every interaction, 3did identifies and groups different binding modes by clustering
        similar interfaces into 'interaction topologies'.
      notes: Interface residue patches cluster into conserved binding topologies (PMID:24081580) (ECO:0000305)
  - subject: GO:0005515
    predicate: causally upstream of
    predicate_id: RO:0002411
    object: GO:0046983
    description: Complementary inter-chain binding across the interface drives homomeric and heteromeric
      subunit dimerization.
    evidence:
    - reference: PMID:24081580
      snippet: For every interaction, 3did identifies and groups different binding modes by clustering
        similar interfaces into 'interaction topologies'.
      notes: Inter-domain interface binding modes mediate subunit pairing (PMID:24081580) (ECO:0000305)
  - subject: GO:0046983
    predicate: positively regulates
    predicate_id: RO:0002213
    object: GO:0051259
    description: Subunit dimerization and domain-domain interface contacts organize higher-order multiprotein
      oligomerization.
    evidence:
    - reference: PMID:24081580
      snippet: By maintaining a constantly updated collection of domain-based structural interaction templates,
        3did is a reference source of information for the structural characterization of protein interaction
        networks.
      notes: Domain interface templates drive oligomeric complex assembly (PMID:24081580) (ECO:0000305)
evidence:
- reference: PMID:24081580
  notes: Mosca et al. (2014) classify structural domain-domain and domain-motif interfaces into conserved
    interaction topologies in 3did.""",
    },
]


def slug_for(term: str) -> str:
    return term.lower().replace("_", "-")


def yaml_for(entry: dict) -> str:
    lines: list[str] = []
    lines.append(f"identifier: proteintraitsmech:{entry['term']}")
    lines.append(f"label: {entry['label']}")
    lines.append("definition: >-")
    lines.append(f"  {entry['definition']}")
    lines.append(f"definition_source: {DEFINITION_SOURCE}")
    lines.append("trait_axis: STRUCTURE")
    lines.append(f"trait_category: {entry['category']}")
    lines.append("term_kind: CLASS")
    lines.append("mapping_status: SEEDED")

    if entry["term"] in CHILD_MOTIFS:
        lines.append("parent_traits:")
        lines.append(f"  - {PARENT_MOTIF}")

    xrefs: list[str] = []
    if entry.get("so_xref"):
        xrefs.append(entry["so_xref"])
    xrefs.append(SOURCE_ENUM)
    xrefs.extend(entry.get("extra_xrefs") or [])
    lines.append("xrefs:")
    for x in xrefs:
        lines.append(f"  - {x}")

    if entry.get("extra_blocks"):
        lines.append(entry["extra_blocks"])

    return "\n".join(lines) + "\n"


def target_path(entry: dict) -> Path:
    return DATA_DIR / entry["subdir"] / f"{slug_for(entry['term'])}.yaml"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write YAMLs (default: dry-run)")
    parser.add_argument("--force", action="store_true", help="overwrite existing files when applying")
    args = parser.parse_args()

    counts: dict[str, int] = {}
    written = 0
    skipped = 0
    would_overwrite = 0

    for entry in TERMS:
        path = target_path(entry)
        rel = path.relative_to(REPO_ROOT)
        counts[entry["category"]] = counts.get(entry["category"], 0) + 1

        if path.exists() and not args.force:
            action = "SKIP (exists)"
            skipped += 1
        elif path.exists() and args.force:
            action = "OVERWRITE" if args.apply else "would-overwrite"
            if args.apply:
                write_record(path, yaml_for(entry))
                written += 1
            else:
                would_overwrite += 1
        else:
            action = "WRITE" if args.apply else "would-write"
            if args.apply:
                path.parent.mkdir(parents=True, exist_ok=True)
                write_record(path, yaml_for(entry))
                written += 1

        print(f"  [{action:16s}] {rel}")

    print()
    print("Per-category totals:")
    for cat, n in sorted(counts.items()):
        print(f"  {cat:22s} {n}")
    print()
    if args.apply:
        print(f"Wrote {written} file(s); skipped {skipped} existing.")
    else:
        planned = len(TERMS) - skipped
        print(f"Dry-run — would write {planned} file(s); {skipped} already exist.")
        if would_overwrite:
            print(f"  (of which {would_overwrite} would be overwritten by --force)")
        print("Re-run with --apply to write.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
