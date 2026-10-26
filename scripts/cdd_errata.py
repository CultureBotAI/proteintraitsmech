"""Accession-scoped, evidence-backed NCBI CDD source-definition errata.

Shared by `seed_cdd.py` and `repair_cdd_errata.py`; this is not a global prose
replacement. Each entry corresponds to one Stage 4 scientific review finding
(`F1` through `F18`, tracked in #1171, #1172, and #1188) on an NCBI CDD
`SEQ_DOMAIN` record. Sixteen targets (`F3` through `F12` in #1171, and `F13`
through `F18` in #1188) had zero qualified occurrences at repair time; the two
remaining Stage 4 targets (`F1` on `CDD:cd00104` and `F2` on `CDD:cd00959`,
#1172) carried qualified occurrences whose `record_sha256` receipts in
`data/grounding/qualified_record_bindings.jsonl.d/` are transactionally
re-bound by `repair_cdd_errata.py`.

Unexpected upstream wording, short names, or superfamily parentage must be
re-reviewed rather than silently overwritten. No protein qualification is
conferred.
"""

from __future__ import annotations

from dataclasses import dataclass

from yaml_emit import yaml_escape

CURATION_TIMESTAMP = "2026-10-22T07:35:00Z"
CYCLE2_CURATION_TIMESTAMP = "2026-10-25T23:10:00Z"


@dataclass(frozen=True)
class CddErratum:
    accession: str
    finding_id: str
    label: str
    parent: str
    rel_path: str
    source_description: str
    replacements: tuple[tuple[str, str], ...]
    definition_source: str
    evidence: tuple[tuple[str, str, str], ...]
    event_action: str
    event_changes: str
    curation_timestamp: str = CURATION_TIMESTAMP

    @property
    def identifier(self) -> str:
        return f"CDD:{self.accession}"

    @property
    def corrected_description(self) -> str:
        text = self.source_description
        for old, new in self.replacements:
            if text.count(old) != 1:
                raise ValueError(
                    f"{self.accession}: expected replacement target {old!r} once"
                )
            text = text.replace(old, new)
        return text


ERRATA: dict[str, CddErratum] = {
    "cd00104": CddErratum(
        accession="cd00104",
        finding_id="F1",
        label="KAZAL_FS",
        parent="cl00097",
        rel_path=(
            "sequence/domain/cdd/"
            "kazal-type-serine-protease-inhibitors-and-follistatin-like-domains-kaz-cd00104.yaml"
        ),
        source_description=(
            "Kazal type serine protease inhibitors and follistatin-like domains. "
            "Kazal inhibitors inhibit serine proteases, such as, trypsin, "
            "chyomotrypsin, avian ovomucoids, and elastases. The inhibitory domain "
            "has one reactive site peptide bond, which serves the cognate enzyme as "
            "substrate. The reactive site peptide bond is a combining loop which "
            "has an identical conformation in all Kazal inhibitors and in all "
            "enzyme/inhibitor complexes. These Kazal domains (small hydrophobic "
            "core of alpha/beta structure with 3 to 4 disulfide bonds) often occur "
            "in tandem arrays. Similar domains are also present in follistatin (FS) "
            "and follistatin-like family members, which play an important role in "
            "tissue specific regulation. The FS domain consists of an N-terminal "
            "beta hairpin (FOLN/EGF-like domain) and a Kazal-like domain and has "
            "five disulfide bonds. Although the Kazal-like FS substructure is "
            "similar to Kazal proteinase inhibitors, no FS domain has yet been "
            "shown to be a proteinase inhibitor. Follistatin-like family members "
            "include SPARC, also known as, BM-40 or osteonectin, the Gallus gallus "
            "Flik protein, as well as, agrin which has a long array of FS domains. "
            "The kazal-type inhibitor domain has also been detected in an "
            "extracellular loop region of solute carrier 21 (SLC21) family members "
            "(organic anion transporters) , which may regulate the specificity of "
            "anion uptake. The distant homolog, Ascidian trypsin inhibitor, is "
            "included in this CD"
        ),
        replacements=(
            (
                "Kazal inhibitors inhibit serine proteases, such as, trypsin, "
                "chyomotrypsin, avian ovomucoids, and elastases.",
                "Kazal inhibitors (such as avian ovomucoids and pancreatic "
                "secretory trypsin inhibitor) inhibit serine proteases such as "
                "trypsin, chymotrypsin, and elastases.",
            ),
        ),
        definition_source=(
            "NCBI CDD; PTM source-definition erratum #1172 "
            "(Stage 4 finding F1; PMID:6192856; UniProtKB:P00995)"
        ),
        evidence=(
            (
                "PMID:6192856",
                "Three-dimensional structure of the complex between the serine proteinase, Streptomyces griseus proteinase B, and the third domain of the Kazal-type ovomucoid inhibitor from turkey",
                "Bolognesi et al. (1982, J Mol Biol 162:839-868) establish that "
                "avian ovomucoids are multi-domain Kazal-type serine protease "
                "inhibitor proteins rather than target serine proteases, and "
                "correct the upstream 'chyomotrypsin' spelling error.",
            ),
        ),
        event_action="source_erratum_cd00104",
        event_changes=(
            "Corrected the 'chyomotrypsin' spelling error and clarified that "
            "avian ovomucoids are Kazal-type serine protease inhibitor proteins "
            "rather than target serine proteases (#1172, Stage 4 finding F1)."
        ),
    ),
    "cd00959": CddErratum(
        accession="cd00959",
        finding_id="F2",
        label="DeoC",
        parent="cl21457",
        rel_path=(
            "sequence/domain/cdd/"
            "2-deoxyribose-5-phosphate-aldolase-dera-of-the-deoc-family-2-deoxyribo-cd00959.yaml"
        ),
        source_description=(
            "2-deoxyribose-5-phosphate aldolase (DERA) of the DeoC family. "
            "2-deoxyribose-5-phosphate aldolase (DERA) of the DeoC family. DERA "
            "belongs to the class I aldolases and catalyzes a reversible aldol "
            "reaction between acetaldehyde and glyceraldehyde 3-phosphate to "
            "generate 2-deoxyribose 5-phosphate. DERA is unique in catalyzing the "
            "aldol reaction between two aldehydes, and its broad substrate "
            "specificity confers considerable utility as a biocatalyst, offering an "
            "environmentally benign alternative to chiral transition metal "
            "catalysis of the asymmetric aldol reaction"
        ),
        replacements=(
            (
                "2-deoxyribose-5-phosphate aldolase (DERA) of the DeoC family. "
                "2-deoxyribose-5-phosphate aldolase (DERA) of the DeoC family.",
                "2-deoxyribose-5-phosphate aldolase (DERA) of the DeoC family.",
            ),
        ),
        definition_source=(
            "NCBI CDD; PTM source-definition erratum #1172 "
            "(Stage 4 finding F2; PMID:11305920; UniProtKB:P0A6L0)"
        ),
        evidence=(
            (
                "PMID:11305920",
                "Crystal structure of Escherichia coli 2-deoxyribose-5-phosphate aldolase (DeoC) at 0.99 A resolution",
                "Heine et al. (2001, Science 294:369-374) and UniProtKB:P0A6L0 "
                "(DeoC) characterize 2-deoxyribose-5-phosphate aldolase (DERA) of "
                "the DeoC family; the erratum removes the duplicated opening title "
                "sentence from the upstream CDD description.",
            ),
        ),
        event_action="source_erratum_cd00959",
        event_changes=(
            "Removed the duplicated opening title sentence "
            "'2-deoxyribose-5-phosphate aldolase (DERA) of the DeoC family.' from "
            "the upstream CDD description (#1172, Stage 4 finding F2)."
        ),
    ),
    "cd09530": CddErratum(
        accession="cd09530",
        finding_id="F3",
        label="SAM_Samd14",
        parent="cl15755",
        rel_path=(
            "sequence/domain/cdd/"
            "sam-domain-of-samd14-subfamily-sam-sterile-alpha-motif-domain-of-samd1-cd09530.yaml"
        ),
        source_description=(
            "SAM domain of Samd14 subfamily. SAM (sterile alpha motif) domain of "
            "SamD14 (or FAM15A) subfamily is a putative protein-protein interaction "
            "domain. SAM is widespread domain in proteins involved in signal "
            "transduction and regulation. In many cases SAM mediates "
            "homodimerization/oligomerization. The exact function of proteins "
            "belonging to this subfamily is unknown"
        ),
        replacements=(
            (
                "SAM (sterile alpha motif) domain of SamD14 (or FAM15A) subfamily "
                "is a putative protein-protein interaction domain.",
                "SAM (sterile alpha motif) domain of the SAMD15 (formerly FAM15A; "
                "distinct from human SAMD14 in CDD:cd09512) subfamily is a putative "
                "protein-protein interaction domain.",
            ),
        ),
        definition_source=(
            "NCBI CDD; PTM source-definition erratum #1171 "
            "(Stage 4 finding F3; UniProtKB:Q9P1V8; HGNC:20263)"
        ),
        evidence=(
            (
                "UniProtKB:Q9P1V8",
                "Gene Name: SAMD15; Synonyms: C14orf174, FAM15A; DR CDD; cd09530; SAM_Samd14; 1.",
                "Reviewed human UniProtKB/Swiss-Prot entry Q9P1V8 (SAMD15, HGNC:20263) "
                "carries the legacy synonym FAM15A and is annotated with CDD:cd09530 "
                "(SAM_Samd14), whereas canonical human SAMD14 (UniProtKB:Q8IZD0, "
                "HGNC:24606) is annotated with CDD:cd09512 (SAM_2_SAMD14).",
            ),
        ),
        event_action="source_erratum_cd09530",
        event_changes=(
            "Disambiguated the legacy FAM15A alias in the CDD:cd09530 description "
            "as human SAMD15 (UniProtKB:Q9P1V8, HGNC:20263), distinct from human "
            "SAMD14 in CDD:cd09512 (#1171, Stage 4 finding F3). Retained the "
            "source label SAM_Samd14 and superfamily parent CDD:cl15755."
        ),
    ),
    "cd13344": CddErratum(
        accession="cd13344",
        finding_id="F4",
        label="PH-GRAM_MTMR7",
        parent="cl17171",
        rel_path=(
            "sequence/domain/cdd/"
            "myotubularian-mtm-related-7-protein-mtmr7-pleckstrin-homology-glucosyl-cd13344.yaml"
        ),
        source_description=(
            "Myotubularian (MTM) related 7 protein (MTMR7) Pleckstrin "
            "Homology-Glucosyltransferases, Rab-like GTPase activators and "
            "Myotubularins (PH-GRAM) domain. MTMR7 is a member of the myotubularin "
            "dual specificity protein phosphatase gene family. MTMR6 binds to "
            "phosphoinositide lipids through its PH-GRAM domain and can hydrolyze "
            "phosphatidylinositol(3)-phosphate and "
            "phosphatidylinositol(3,5)-biphosphate. MTMR7 interacts with MTMR6, "
            "MTMR8 and MTMR9. MTMR7 contains a N-terminal PH-GRAM domain, a "
            "Rac-induced recruitment domain (RID) domain, an active PTP domain, a "
            "SET-interaction domain, and a C-terminal coiled-coil region. "
            "Myotubularin-related proteins are a subfamily of protein tyrosine "
            "phosphatases (PTPs) that dephosphorylate D3-phosphorylated inositol "
            "lipids. Mutations in this family cause the human neuromuscular "
            "disorders myotubular myopathy and type 4B Charcot-Marie-Tooth "
            "syndrome. 6 of the 13 MTMRs (MTMRs 5, 9-13) contain naturally "
            "occurring substitutions of residues required for catalysis by PTP "
            "family enzymes. Although these proteins are predicted to be "
            "enzymatically inactive, they are thought to function as antagonists of "
            "endogenous phosphatase activity or interaction modules. Most MTMRs "
            "contain a N-terminal PH-GRAM domain, a Rac-induced recruitment domain "
            "(RID) domain, a PTP domain (which may be active or inactive), a "
            "SET-interaction domain, and a C-terminal coiled-coil region. In "
            "addition some members contain DENN domain N-terminal to the PH-GRAM "
            "domain and FYVE, PDZ, and PH domains C-terminal to the coiled-coil "
            "region. The GRAM domain, found in myotubularins, "
            "glucosyltransferases, and other putative membrane-associated proteins, "
            "is part of a larger motif with a pleckstrin homology (PH) domain fold. "
            "The PH domain family possesses multiple functions including the "
            "ability to bind phosphoinositides via its beta1/beta2, beta3/beta4, "
            "and beta6/beta7 connecting loops and to other proteins. However, no "
            "phosphoinositide binding sites have been found for the MTMRs to date"
        ),
        replacements=(
            (
                "Myotubularian (MTM) related 7 protein (MTMR7)",
                "Myotubularin (MTM) related 7 protein (MTMR7)",
            ),
            (
                "MTMR6 binds to phosphoinositide lipids through its PH-GRAM domain "
                "and can hydrolyze phosphatidylinositol(3)-phosphate and "
                "phosphatidylinositol(3,5)-biphosphate. MTMR7 interacts with MTMR6, "
                "MTMR8 and MTMR9.",
                "MTMR7 dephosphorylates phosphatidylinositol 3-phosphate (PtdIns3P) "
                "and inositol 1,3-bisphosphate (Ins(1,3)P2) and forms a functional "
                "heterodimer with the catalytically inactive myotubularin MTMR9 "
                "(whereas the closely related subgroup member MTMR6 hydrolyzes "
                "PtdIns3P and PtdIns(3,5)P2).",
            ),
            (
                "However, no phosphoinositide binding sites have been found for the "
                "MTMRs to date",
                "In myotubularins, the PH-GRAM domain mediates phosphoinositide "
                "binding and membrane localization",
            ),
        ),
        definition_source=(
            "NCBI CDD; PTM source-definition erratum #1171 "
            "(Stage 4 finding F4; PMID:11956206; PMID:14690594; UniProtKB:Q9Y216)"
        ),
        evidence=(
            (
                "PMID:11956206",
                "MTMR7 specifically dephosphorylates PtdIns(3)P and Ins(1,3)P2 and interacts with MTMR9",
                "Mochizuki & Majerus (2003, J Biol Chem 278:21856-21863) characterize "
                "MTMR7 (UniProtKB:Q9Y216) as a 3-phosphatase acting on PtdIns3P and "
                "Ins(1,3)P2 in complex with MTMR9, correcting the pasted MTMR6 "
                "sentence in the upstream CDD description.",
            ),
            (
                "PMID:14690594",
                "The PH-GRAM domain of myotubularin binds phosphoinositides",
                "Begley et al. (2003, Mol Cell 12:1391-1402) and Tsujita et al. "
                "(2004, J Biol Chem 279:13817-13824, PMID:14722085) establish "
                "phosphoinositide binding by myotubularin PH-GRAM domains, resolving "
                "the internal contradiction in the trailing upstream sentence.",
            ),
        ),
        event_action="source_erratum_cd13344",
        event_changes=(
            "Corrected 'Myotubularian' typo to 'Myotubularin', replaced the "
            "misplaced MTMR6 substrate/interaction sentence with MTMR7's "
            "PtdIns3P/Ins(1,3)P2 substrate specificity and MTMR9 heterodimer "
            "interaction (PMID:11956206), and resolved the self-contradictory "
            "trailing PH-GRAM phosphoinositide-binding sentence (#1171, Stage 4 "
            "finding F4)."
        ),
    ),
    "cd14999": CddErratum(
        accession="cd14999",
        finding_id="F5",
        label="7tmA_UII-R",
        parent="cl28897",
        rel_path=(
            "sequence/domain/cdd/"
            "urotensin-ii-receptor-member-of-the-class-a-family-of-seven-transmembr-cd14999.yaml"
        ),
        source_description=(
            "urotensin-II receptor, member of the class A family of "
            "seven-transmembrane G protein-coupled receptors. The urotensin-II "
            "receptor (UII-R, also known as the hypocretin receptor) is a member of "
            "the class A rhodopsin-like G-protein coupled receptors, which binds the "
            "peptide hormone urotensin-II. Urotensin II (UII) is a vasoactive "
            "somatostatin-like or cortistatin-like peptide hormone. However, despite "
            "the apparent structural similarity to these peptide hormones, they are "
            "not homologous to UII. Urotensin II was first identified in fish spinal "
            "cord, but later found in humans and other mammals. In fish, UII is "
            "secreted at the back part of the spinal cord, in a neurosecretory "
            "centre called uroneurapophysa, and is involved in the regulation of the "
            "renal and cardiovascular systems. In mammals, urotensin II is the most "
            "potent mammalian vasoconstrictor identified to date and causes "
            "contraction of arterial blood vessels, including the thoracic aorta. "
            "The urotensin II receptor is a rhodopsin-like G-protein coupled "
            "receptor, which binds urotensin-II. The receptor was previously known "
            "as GPR14, or sensory epithelial neuropeptide-like receptor (SENR). The "
            "UII receptor is expressed in the CNS (cerebellum and spinal cord), "
            "skeletal muscle, pancreas, heart, endothelium and vascular smooth "
            "muscle. It is involved in the pathophysiological control of "
            "cardiovascular function and may also influence CNS and endocrine "
            "functions. Binding of urotensin II to the receptor leads to activation "
            "of phospholipase C, through coupling to G(q/11) family proteins. The "
            "resulting increase in intracellular calcium may cause the contraction "
            "of vascular smooth muscle"
        ),
        replacements=(
            (
                "(UII-R, also known as the hypocretin receptor)",
                "(UTS2R, also known as UII-R or GPR14; distinct from the "
                "orexin/hypocretin receptors HCRTR1/HCRTR2 in CDD:cd15208)",
            ),
            (
                "In mammals, urotensin II is the most potent mammalian "
                "vasoconstrictor identified to date and causes contraction of "
                "arterial blood vessels, including the thoracic aorta.",
                "In mammalian isolated arterial preparations such as rat thoracic "
                "aorta, urotensin-II acts as a potent experimental vasoconstrictor, "
                "with vascular responses varying by species and vessel bed.",
            ),
        ),
        definition_source=(
            "NCBI CDD; PTM source-definition erratum #1171 "
            "(Stage 4 finding F5; #952; PMID:10497709; UniProtKB:Q9UKP6)"
        ),
        evidence=(
            (
                "PMID:10497709",
                "Human urotensin-II is a potent vasoconstrictor and ligand for the orphan receptor GPR14",
                "Ames et al. (1999, Nature 401:282-286) identify GPR14/UTS2R "
                "(UniProtKB:Q9UKP6, HGNC:4468) as the urotensin-II receptor and "
                "characterize its potent vasoconstrictor activity in isolated "
                "mammalian arterial rings; hypocretin/orexin receptors (HCRTR1/HCRTR2) "
                "are a distinct GPCR family modeled in CDD:cd15208.",
            ),
        ),
        event_action="source_erratum_cd14999",
        event_changes=(
            "Removed the false 'hypocretin receptor' synonym from CDD:cd14999 "
            "(distinguishing UTS2R/GPR14 from HCRTR1/HCRTR2 in CDD:cd15208) and "
            "qualified the vasoconstrictor potency statement to experimental "
            "mammalian arterial preparations (#1171, #952, Stage 4 finding F5)."
        ),
    ),
    "cd15885": CddErratum(
        accession="cd15885",
        finding_id="F14",
        label="SNARE_SNAP25C",
        parent="cl22856",
        rel_path=(
            "sequence/domain/cdd/"
            "c-terminal-snare-motif-of-snap25-c-terminal-snare-motifs-of-snap25-a-m-cd15885.yaml"
        ),
        source_description=(
            "C-terminal SNARE motif of SNAP25. C-terminal SNARE motifs of SNAP25, "
            "a member of the Qb/Qc subfamily of SNARE (soluble "
            "N-ethylmaleimide-sensitive factor attachment protein receptor) "
            "proteins. SNAP25 interacts with Syntaxin-1 (Qa) and the R-SNARE VAMP2 "
            "(also called synaptobrevin-2). The complex plays a role in transport "
            "of secretory granule from trans-Golgi network to the plasma membrane. "
            "Qb/Qc SNAREs consist of 2 coiled-coil helices (called SNARE motifs, one "
            "belonging to the Qb subgroup and one belonging to the Qc subgroup), "
            "which mediate the interactions with other SNARE proteins, and a "
            "transmembrane domain. In general, the SNARE complex mediates membrane "
            "fusion, important for trafficking of newly synthesized proteins, "
            "recycling of pre-existing proteins and organelle formation. SNARE "
            "proteins are classified into four groups, Qa-, Qb-, Qc- and R-SNAREs, "
            "depending on whether the residue in the hydrophilic center layer of "
            "the four-helical bundle is a glutamine (Q) or arginine (R). Qa-, as "
            "well as Qb- and Qc-SNAREs, are localized to target organelle "
            "membranes, while R-SNARE is localized to vesicle membranes. They form "
            "unique complexes consisting of one member of each subgroup, that "
            "mediate fusion between a specific type of vesicles and their target "
            "organelle. Their SNARE motifs form twisted and parallel "
            "heterotetrameric helix bundles. Other members of the Qb/Qc SNAREs are "
            "SNAP23, SNAP29, SNAP47 and SEC9"
        ),
        replacements=(
            (
                ", which mediate the interactions with other SNARE proteins, and a "
                "transmembrane domain.",
                ", which mediate the interactions with other SNARE proteins, and "
                "lack a transmembrane domain; SNAP25 is anchored to target membranes "
                "via palmitoylated cysteine residues in the linker between its two "
                "SNARE motifs.",
            ),
        ),
        definition_source=(
            "NCBI CDD; PTM source-definition erratum #1188 "
            "(Cycle 2 Stage 4 finding F14; PMID:9759094; UniProtKB:P60880)"
        ),
        evidence=(
            (
                "PMID:9759094",
                "Four parallel alpha-helices... SNAP-25 contributes two helices (Sn1 and Sn2) connected by a palmitoylated linker and lacks a transmembrane anchor",
                "Sutton et al. (1998, Nature 395:347-353) and UniProtKB:P60880 "
                "(SNAP25) establish that Qbc-SNAREs (SNAP25, SNAP23, SNAP29, SNAP47, "
                "Sec9) contribute both Qb and Qc SNARE motifs and lack a "
                "transmembrane domain, with SNAP25 anchored to membranes via "
                "S-palmitoylated cysteine residues in its inter-motif linker.",
            ),
        ),
        event_action="source_erratum_cd15885",
        event_changes=(
            "Corrected the false statement that Qb/Qc SNAREs contain a "
            "transmembrane domain: SNAP25 and Qb/Qc SNAREs lack a transmembrane "
            "domain, and SNAP25 is membrane-anchored via palmitoylated cysteines "
            "in the linker between its two SNARE motifs (#1188, Cycle 2 Stage 4 "
            "finding F14)."
        ),
        curation_timestamp=CYCLE2_CURATION_TIMESTAMP,
    ),
    "cd15894": CddErratum(
        accession="cd15894",
        finding_id="F6",
        label="SNARE_SNAP25N",
        parent="cl22856",
        rel_path=(
            "sequence/domain/cdd/"
            "n-terminal-snare-motif-of-snap25-n-terminal-snare-motifs-of-snap25-a-m-cd15894.yaml"
        ),
        source_description=(
            "N-terminal SNARE motif of SNAP25. N-terminal SNARE motifs of SNAP25, "
            "a member of the Qb/Qc subfamily of SNARE (soluble "
            "N-ethylmaleimide-sensitive factor attachment protein receptor) "
            "proteins. SNAP25 interacts with Syntaxin-1 (Qa) and the R-SNARE VAMP2 "
            "(also called synaptobrevin-2). The complex plays a role in transport "
            "of secretory granule from trans-Golgi network to the plasma membrane. "
            "Qb/Qc SNAREs consist of 2 coiled-coil helices (called SNARE motifs, one "
            "belonging to the Qb subgroup and one belonging to the Qc subgroup), "
            "which mediate the interactions with other SNARE proteins, and a "
            "transmembrane domain. In general, the SNARE complex mediates membrane "
            "fusion, important for trafficking of newly synthesized proteins, "
            "recycling of pre-existing proteins and organelle formation. SNARE "
            "proteins are classified into four groups, Qa-, Qb-, Qc- and R-SNAREs, "
            "depending on whether the residue in the hydrophilic center layer of "
            "the four-helical bundle is a glutamine (Q) or arginine (R). Qa-, as "
            "well as Qb- and Qc-SNAREs, are localized to target organelle "
            "membranes, while R-SNARE is localized to vesicle membranes. They form "
            "unique complexes consisting of one member of each subgroup, that "
            "mediate fusion between a specific type of vesicles and their target "
            "organelle. Their SNARE motifs form twisted and parallel "
            "heterotetrameric helix bundles. Other members of the Qb/Qc SNAREs are "
            "SNAP23, SNAP29, SNAP47 and SEC9"
        ),
        replacements=(
            (
                ", which mediate the interactions with other SNARE proteins, and a "
                "transmembrane domain.",
                ", which mediate the interactions with other SNARE proteins, and "
                "lack a transmembrane domain; SNAP25 is anchored to target membranes "
                "via palmitoylated cysteine residues in the linker between its two "
                "SNARE motifs.",
            ),
        ),
        definition_source=(
            "NCBI CDD; PTM source-definition erratum #1171 "
            "(Stage 4 finding F6; PMID:9759094; UniProtKB:P60880)"
        ),
        evidence=(
            (
                "PMID:9759094",
                "Four parallel alpha-helices... SNAP-25 contributes two helices (Sn1 and Sn2) connected by a palmitoylated linker and lacks a transmembrane anchor",
                "Sutton et al. (1998, Nature 395:347-353) and UniProtKB:P60880 "
                "(SNAP25) establish that Qbc-SNAREs (SNAP25, SNAP23, SNAP29, SNAP47, "
                "Sec9) contribute both Qb and Qc SNARE motifs and lack a "
                "transmembrane domain, with SNAP25 anchored to membranes via "
                "S-palmitoylated cysteine residues in its inter-motif linker.",
            ),
        ),
        event_action="source_erratum_cd15894",
        event_changes=(
            "Corrected the false statement that Qb/Qc SNAREs contain a "
            "transmembrane domain: SNAP25 and Qb/Qc SNAREs lack a transmembrane "
            "domain, and SNAP25 is membrane-anchored via palmitoylated cysteines "
            "in the linker between its two SNARE motifs (#1171, Stage 4 finding F6)."
        ),
    ),
    "cd16523": CddErratum(
        accession="cd16523",
        finding_id="F7",
        label="RING-HC_MYLIP",
        parent="cl17238",
        rel_path=(
            "sequence/domain/cdd/"
            "ring-finger-hc-subclass-found-in-myosin-regulatory-light-chain-interac-cd16523.yaml"
        ),
        source_description=(
            "RING finger, HC subclass, found in myosin regulatory light chain "
            "interacting protein (MYLIP) and similar proteins. MYLIP, also known as "
            "inducible degrader of the low-density lipoprotein (LDL)-receptor "
            "(IDOL), or MIR, is an E3 ubiquitin-protein ligase that mediates "
            "ubiquitination and subsequent proteasomal degradation of myosin "
            "regulatory light chain (MRLC), LDLR, VLDLR, and LRP8. Its activity "
            "depends on E2 ubiquitin-conjugating enzymes of the UBE2D family. MYLIP "
            "stimulates clathrin-independent endocytosis and acts as a "
            "sterol-dependent inhibitor of cellular cholesterol uptake by binding "
            "directly to the cytoplasmic tail of the LDLR and promoting its "
            "ubiquitination via the UBE2D1/E1 complex. The ubiquitinated LDLR then "
            "enters the multivesicular body (MVB) protein-sorting pathway and is "
            "shuttled to the lysosome for degradation. Moreover, MYLIP has been "
            "identified as a novel ERM-like protein that affects cytoskeleton "
            "interactions regulating cell motility, such as neurite outgrowth. The "
            "ERM proteins includes ezrin, radixin, and moesin, which are "
            "cytoskeletal effector proteins linking actin to membrane-bound "
            "proteins at the cell surface. MYLIP contains an ERM-homology domain "
            "and a C-terminal C3HC4-type RING-HC finger"
        ),
        replacements=(
            (
                "mediates ubiquitination and subsequent proteasomal degradation of "
                "myosin regulatory light chain (MRLC), LDLR, VLDLR, and LRP8.",
                "mediates ubiquitination and proteasomal degradation of myosin "
                "regulatory light chain (MRLC) and promotes ubiquitination and "
                "ESCRT/MVB-dependent lysosomal degradation of the lipoprotein "
                "receptors LDLR, VLDLR, and LRP8.",
            ),
        ),
        definition_source=(
            "NCBI CDD; PTM source-definition erratum #1171 "
            "(Stage 4 finding F7; PMID:19520913; PMID:20427281; UniProtKB:Q8WY64)"
        ),
        evidence=(
            (
                "PMID:19520913",
                "Idol is an E3 ubiquitin ligase that triggers ubiquitination of the LDLR on its cytoplasmic domain, thereby targeting it for lysosomal degradation",
                "Zelcer et al. (2009, Science 325:100-104) and Hong et al. (2010, "
                "Arterioscler Thromb Vasc Biol 30:2503-2509, PMID:20427281) show "
                "that MYLIP/IDOL targets LDLR, VLDLR, and LRP8/ApoER2 for "
                "ESCRT/MVB-dependent lysosomal degradation rather than proteasomal "
                "degradation, resolving the internal contradiction in the CDD text.",
            ),
        ),
        event_action="source_erratum_cd16523",
        event_changes=(
            "Resolved the internal contradiction in CDD:cd16523 by distinguishing "
            "proteasomal degradation of MRLC from ESCRT/MVB-dependent lysosomal "
            "degradation of the lipoprotein receptors LDLR, VLDLR, and LRP8 "
            "(#1171, Stage 4 finding F7)."
        ),
    ),
    "cd16652": CddErratum(
        accession="cd16652",
        finding_id="F8",
        label="dRING_Rmd5p-like",
        parent="cl17238",
        rel_path=(
            "sequence/domain/cdd/"
            "degenerated-ring-dring-finger-found-in-saccharomyces-cerevisiae-requir-cd16652.yaml"
        ),
        source_description=(
            "Degenerated RING (dRING) finger found in Saccharomyces cerevisiae "
            "required for meiotic nuclear division protein 5 (Rmd5p) and similar "
            "proteins. Rmd5p, also known as glucose-induced degradation protein 2 "
            "(Gid2) or sporulation protein RMD5, is an E3 ubiquitin ligase "
            "containing a Lissencephaly type-1-like homology motif (LisH), a "
            "C-terminal to LisH motif (CTLH) domain, and a degenerated RING finger "
            "that is characterized by lacking the second, fifth, and sixth Zn2+ "
            "ion-coordinating residues compared with the classic C3H2C3-/C3HC4-type "
            "RING fingers. It forms the heterodimeric E3 ligase unit of the glucose "
            "induced degradation deficient (GID) complex with Gid9 (also known as "
            "Fyv10), which has a degenerated RING finger as well. The GID complex "
            "triggers polyubiquitylation and subsequent proteasomal degradation of "
            "the gluconeogenic enzymes fructose-1, 6-bisphosphate by fructose-1, "
            "6-bisphosphatase (FBPase), phosphoenolpyruvate carboxykinase (PEPCK), "
            "and cytoplasmic malate dehydrogenase (c-MDH). Moreover, Rmd5p can form "
            "the GID complex with the other six Gid proteins, including Gid1/Vid30, "
            "Gid4/Vid24, Gid5/Vid28, Gid7, Gid8, and Gid9/Fyv10. The GID complex in "
            "which the seven Gid proteins reside functions as a novel ubiquitin "
            "ligase (E3) involved in the regulation of carbohydrate metabolism"
        ),
        replacements=(
            (
                "fructose-1, 6-bisphosphate by fructose-1, 6-bisphosphatase (FBPase)",
                "fructose-1,6-bisphosphatase (FBPase)",
            ),
        ),
        definition_source=(
            "NCBI CDD; PTM source-definition erratum #1171 "
            "(Stage 4 finding F8; PMID:18508924; UniProtKB:Q12508)"
        ),
        evidence=(
            (
                "PMID:18508924",
                "The GID complex is a new ubiquitin ligase (E3) involved in the polyubiquitination and proteasomal degradation of fructose-1,6-bisphosphatase",
                "Santt et al. (2008, Mol Biol Cell 19:3323-3333) show that the "
                "yeast GID E3 ubiquitin ligase complex containing Rmd5p/Gid2 "
                "(UniProtKB:Q12508) polyubiquitylates the gluconeogenic enzyme "
                "fructose-1,6-bisphosphatase (FBPase, Fbp1p), correcting the "
                "garbled phrase 'fructose-1, 6-bisphosphate by fructose-1, "
                "6-bisphosphatase (FBPase)'.",
            ),
        ),
        event_action="source_erratum_cd16652",
        event_changes=(
            "Corrected the garbled phrase 'fructose-1, 6-bisphosphate by "
            "fructose-1, 6-bisphosphatase (FBPase)' to "
            "'fructose-1,6-bisphosphatase (FBPase)' in the list of gluconeogenic "
            "enzymes targeted by the GID E3 ligase complex (#1171, Stage 4 "
            "finding F8)."
        ),
    ),
    "cd17149": CddErratum(
        accession="cd17149",
        finding_id="F17",
        label="DCX1_DCDC2",
        parent="cl28922",
        rel_path=(
            "sequence/domain/cdd/"
            "dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17149.yaml"
        ),
        source_description=(
            "Dublecortin-like domain 1 found in doublecortin domain-containing "
            "protein 2 (DCDC2). DCDC2 is a member of doublecortin (DCX) family. "
            "It is a microtubule-associated protein (MAP) with a stable "
            "ubiquitin-like tertiary fold. Ubiquitin (Ub) is a protein modifier "
            "in eukaryotes that is involved in various cellular processes, "
            "including transcriptional regulation, cell cycle control, and DNA "
            "repair. Microtubules are key components of the cytoskeleton that are "
            "involved in cell movement, shape determination, division and "
            "transport. DCDC2 genetic variation in humans is associated with "
            "reading disability, attention deficit hyperactivity disorder (ADHD), "
            "and difficulties in mathematics. A genetic variant of DCDC2 "
            "associates with dyslexia, a common neurobehavioral disorder of "
            "reading. DCDC2 protein interacts with many of the same cytoskeleton "
            "related proteins that other members of the DCX family interact with"
        ),
        replacements=(
            (
                "Dublecortin-like domain 1 found in doublecortin domain-containing "
                "protein 2 (DCDC2). DCDC2 is a member of doublecortin (DCX) family. "
                "It is a microtubule-associated protein (MAP) with a stable "
                "ubiquitin-like tertiary fold. Ubiquitin (Ub) is a protein modifier "
                "in eukaryotes that is involved in various cellular processes, "
                "including transcriptional regulation, cell cycle control, and DNA "
                "repair.",
                "Doublecortin-like domain 1 found in doublecortin domain-containing "
                "protein 2 (DCDC2). DCDC2 is a member of the doublecortin (DCX) "
                "family. It is a microtubule-associated protein (MAP) with stable "
                "double tandem DCX repeats adopting a ubiquitin-like beta-grasp "
                "tertiary fold.",
            ),
        ),
        definition_source=(
            "NCBI CDD; PTM source-definition erratum #1188 "
            "(Cycle 2 Stage 4 finding F17; PMID:16278295; UniProtKB:Q9UHG0)"
        ),
        evidence=(
            (
                "PMID:16278295",
                "DCDC2 contains a doublecortin peptide domain, similar to the DCX gene mutated in X-linked lissencephaly and double cortex syndrome",
                "Meng et al. (2005, Proc Natl Acad Sci USA 102:17053-17058) and "
                "reviewed human UniProtKB/Swiss-Prot entry Q9UHG0 (DCDC2, HGNC:18141) "
                "characterize DCDC2 as a microtubule-associated protein containing "
                "tandem doublecortin (DCX) domains with a ubiquitin-like beta-grasp "
                "fold, correcting the 'Dublecortin-like' spelling error and removing "
                "the off-target ubiquitin protein-modifier digression.",
            ),
        ),
        event_action="source_erratum_cd17149",
        event_changes=(
            "Corrected the 'Dublecortin-like' spelling error and replaced the "
            "off-target ubiquitin protein-modifier digression with the tandem DCX "
            "ubiquitin-like beta-grasp repeat description (#1188, Cycle 2 Stage 4 "
            "finding F17)."
        ),
        curation_timestamp=CYCLE2_CURATION_TIMESTAMP,
    ),
    "cd17150": CddErratum(
        accession="cd17150",
        finding_id="F9",
        label="DCX1_DCDC2B",
        parent="cl28922",
        rel_path=(
            "sequence/domain/cdd/"
            "dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17150.yaml"
        ),
        source_description=(
            "Dublecortin-like domain 1 found in doublecortin domain-containing "
            "protein 2B (DCDC2B). DCDC2 is a member of doublecortin (DCX) family. "
            "It is a microtubule-associated protein (MAP) with stable double tandem "
            "DCX repeats of ubiquitin-like tertiary fold. Microtubules are key "
            "components of the cytoskeleton that are involved in cell movement, "
            "shape determination, division and transport. DCDC2 genetic variation "
            "in humans is associated with reading disability, attention deficit "
            "hyperactivity disorder (ADHD), and difficulties in mathematics. A "
            "genetic variant of DCDC2 associates with dyslexia, a common "
            "neurobehavioral disorder of reading. DCDC2 protein interacts with many "
            "of the same cytoskeleton related proteins that other members of the "
            "DCX family interact with"
        ),
        replacements=(
            (
                "Dublecortin-like domain 1 found in doublecortin domain-containing "
                "protein 2B (DCDC2B). DCDC2 is a member of doublecortin (DCX) "
                "family. It is a microtubule-associated protein (MAP) with stable "
                "double tandem DCX repeats of ubiquitin-like tertiary fold.",
                "Doublecortin-like domain 1 found in doublecortin domain-containing "
                "protein 2B (DCDC2B). DCDC2B is a member of the doublecortin (DCX) "
                "family closely related to its paralog DCDC2, a "
                "microtubule-associated protein (MAP) with stable double tandem DCX "
                "repeats of ubiquitin-like tertiary fold.",
            ),
            (
                "DCDC2 genetic variation in humans is associated with reading "
                "disability, attention deficit hyperactivity disorder (ADHD), and "
                "difficulties in mathematics. A genetic variant of DCDC2 associates "
                "with dyslexia, a common neurobehavioral disorder of reading.",
                "In the paralogous DCDC2 gene, human genetic variation is "
                "associated with reading disability (dyslexia), attention deficit "
                "hyperactivity disorder (ADHD), and difficulties in mathematics.",
            ),
        ),
        definition_source=(
            "NCBI CDD; PTM source-definition erratum #1171 "
            "(Stage 4 finding F9; UniProtKB:A2VCK2; UniProtKB:Q9UHG0)"
        ),
        evidence=(
            (
                "UniProtKB:A2VCK2",
                "Protein Name: Doublecortin domain-containing protein 2B; Gene Name: DCDC2B; DR CDD; cd17150; DCX1_DCDC2B; 1.",
                "Reviewed human UniProtKB/Swiss-Prot entry A2VCK2 (DCDC2B, "
                "HGNC:33489) carries the N-terminal DCX1 domain modeled by "
                "CDD:cd17150 (DCX1_DCDC2B), whereas human DCDC2 (UniProtKB:Q9UHG0, "
                "HGNC:18141) is a distinct paralog whose N-terminal DCX1 domain is "
                "modeled by CDD:cd17148 (DCX1_DCDC2).",
            ),
        ),
        event_action="source_erratum_cd17150",
        event_changes=(
            "Corrected the 'Dublecortin-like' spelling error and distinguished "
            "DCDC2B (UniProtKB:A2VCK2, modeled by CDD:cd17150) from its paralog "
            "DCDC2 (UniProtKB:Q9UHG0, modeled by CDD:cd17148) in the phenotype "
            "summary (#1171, Stage 4 finding F9)."
        ),
    ),
    "cd17151": CddErratum(
        accession="cd17151",
        finding_id="F15",
        label="DCX1_DCDC2C",
        parent="cl28922",
        rel_path=(
            "sequence/domain/cdd/"
            "dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17151.yaml"
        ),
        source_description=(
            "Dublecortin-like domain 1 found in doublecortin domain-containing "
            "protein 2C (DCDC2C). DCDC2 is a member of doublecortin (DCX) family. "
            "It is a microtubule-associated protein (MAP) with stable double tandem "
            "DCX repeats of ubiquitin-like tertiary fold. Microtubules are key "
            "components of the cytoskeleton that are involved in cell movement, "
            "shape determination, division and transport. DCDC2 genetic variation "
            "in humans is associated with reading disability, attention deficit "
            "hyperactivity disorder (ADHD), and difficulties in mathematics. A "
            "genetic variant of DCDC2 associates with dyslexia, a common "
            "neurobehavioral disorder of reading. DCDC2 protein interacts with many "
            "of the same cytoskeleton related proteins that other members of the "
            "DCX family interact with"
        ),
        replacements=(
            (
                "Dublecortin-like domain 1 found in doublecortin domain-containing "
                "protein 2C (DCDC2C). DCDC2 is a member of doublecortin (DCX) "
                "family. It is a microtubule-associated protein (MAP) with stable "
                "double tandem DCX repeats of ubiquitin-like tertiary fold.",
                "Doublecortin-like domain 1 found in doublecortin domain-containing "
                "protein 2C (DCDC2C). DCDC2C is a member of the doublecortin (DCX) "
                "family closely related to its paralog DCDC2, a "
                "microtubule-associated protein (MAP) with stable double tandem DCX "
                "repeats of ubiquitin-like tertiary fold.",
            ),
            (
                "DCDC2 genetic variation in humans is associated with reading "
                "disability, attention deficit hyperactivity disorder (ADHD), and "
                "difficulties in mathematics. A genetic variant of DCDC2 associates "
                "with dyslexia, a common neurobehavioral disorder of reading.",
                "In the paralogous DCDC2 gene, human genetic variation is "
                "associated with reading disability (dyslexia), attention deficit "
                "hyperactivity disorder (ADHD), and difficulties in mathematics.",
            ),
        ),
        definition_source=(
            "NCBI CDD; PTM source-definition erratum #1188 "
            "(Cycle 2 Stage 4 finding F15; UniProtKB:A8MYV0; UniProtKB:Q9UHG0)"
        ),
        evidence=(
            (
                "UniProtKB:A8MYV0",
                "Protein Name: Doublecortin domain-containing protein 2C; Gene Name: DCDC2C; DR CDD; cd17151; DCX1_DCDC2C; 1.",
                "Reviewed human UniProtKB/Swiss-Prot entry A8MYV0 (DCDC2C, "
                "HGNC:33863) carries the N-terminal DCX1 domain modeled by "
                "CDD:cd17151 (DCX1_DCDC2C), whereas human DCDC2 (UniProtKB:Q9UHG0, "
                "HGNC:18141) is a distinct paralog whose N-terminal DCX1 domain is "
                "modeled by CDD:cd17149 (DCX1_DCDC2).",
            ),
        ),
        event_action="source_erratum_cd17151",
        event_changes=(
            "Corrected the 'Dublecortin-like' spelling error and distinguished "
            "DCDC2C (UniProtKB:A8MYV0, modeled by CDD:cd17151) from its paralog "
            "DCDC2 (UniProtKB:Q9UHG0, modeled by CDD:cd17149) in the phenotype "
            "summary (#1188, Cycle 2 Stage 4 finding F15)."
        ),
        curation_timestamp=CYCLE2_CURATION_TIMESTAMP,
    ),
    "cd17154": CddErratum(
        accession="cd17154",
        finding_id="F16",
        label="DCX2_DCDC2C",
        parent="cl28922",
        rel_path=(
            "sequence/domain/cdd/"
            "doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17154.yaml"
        ),
        source_description=(
            "Doublecortin-like domain 2 found in doublecortin domain-containing "
            "protein 2C (DCDC2C). DCDC2 is a member of the doublecortin (DCX) "
            "family. It is a microtubule-associated protein (MAP) with stable "
            "double tandem DCX repeats of a ubiquitin-like tertiary fold. "
            "Microtubules are key components of cytoskeleton that are involved in "
            "cell movement, shape determination, division and transport. DCDC2 "
            "genetic variation in humans is associated with reading disability, "
            "attention deficit hyperactivity disorder (ADHD), and difficulties in "
            "mathematics. A genetic variant of DCDC2 associates with dyslexia, a "
            "common neurobehavioral disorder of reading. DCDC2 protein interacts "
            "with many of the same cytoskeleton related proteins that other "
            "members of the DCX family interact with"
        ),
        replacements=(
            (
                "Doublecortin-like domain 2 found in doublecortin domain-containing "
                "protein 2C (DCDC2C). DCDC2 is a member of the doublecortin (DCX) "
                "family. It is a microtubule-associated protein (MAP) with stable "
                "double tandem DCX repeats of a ubiquitin-like tertiary fold.",
                "Doublecortin-like domain 2 found in doublecortin domain-containing "
                "protein 2C (DCDC2C). DCDC2C is a member of the doublecortin (DCX) "
                "family closely related to its paralog DCDC2, a "
                "microtubule-associated protein (MAP) with stable double tandem DCX "
                "repeats of a ubiquitin-like tertiary fold.",
            ),
            (
                "DCDC2 genetic variation in humans is associated with reading "
                "disability, attention deficit hyperactivity disorder (ADHD), and "
                "difficulties in mathematics. A genetic variant of DCDC2 associates "
                "with dyslexia, a common neurobehavioral disorder of reading.",
                "In the paralogous DCDC2 gene, human genetic variation is "
                "associated with reading disability (dyslexia), attention deficit "
                "hyperactivity disorder (ADHD), and difficulties in mathematics.",
            ),
        ),
        definition_source=(
            "NCBI CDD; PTM source-definition erratum #1188 "
            "(Cycle 2 Stage 4 finding F16; UniProtKB:A8MYV0; UniProtKB:Q9UHG0)"
        ),
        evidence=(
            (
                "UniProtKB:A8MYV0",
                "Protein Name: Doublecortin domain-containing protein 2C; Gene Name: DCDC2C; DR CDD; cd17154; DCX2_DCDC2C; 1.",
                "Reviewed human UniProtKB/Swiss-Prot entry A8MYV0 (DCDC2C, "
                "HGNC:33863) carries the C-terminal DCX2 domain modeled by "
                "CDD:cd17154 (DCX2_DCDC2C), whereas human DCDC2 (UniProtKB:Q9UHG0, "
                "HGNC:18141) is a distinct paralog whose C-terminal DCX2 domain is "
                "modeled by CDD:cd17152 (DCX2_DCDC2).",
            ),
        ),
        event_action="source_erratum_cd17154",
        event_changes=(
            "Distinguished DCDC2C (UniProtKB:A8MYV0, modeled by CDD:cd17154) from "
            "its paralog DCDC2 (UniProtKB:Q9UHG0, modeled by CDD:cd17152) in the "
            "domain description and human genetics phenotype summary (#1188, "
            "Cycle 2 Stage 4 finding F16)."
        ),
        curation_timestamp=CYCLE2_CURATION_TIMESTAMP,
    ),
    "cd18592": CddErratum(
        accession="cd18592",
        finding_id="F10",
        label="ABC_6TM_MRP5_8_9_D1",
        parent="cl38913",
        rel_path=(
            "sequence/domain/cdd/"
            "six-transmembrane-helical-domain-1-tmd1-of-multidrug-resistance-associ-cd18592.yaml"
        ),
        source_description=(
            "Six-transmembrane helical domain 1 (TMD1) of multidrug "
            "resistance-associated proteins (MRPs) 5, 8, and 9. This group "
            "represents the six-transmembrane domain 1 (TMD1) of multidrug "
            "resistance-associated proteins (MRPs) 5, 8, and 9, all of which are "
            "belonging to the subfamily C of the ATP-binding cassette (ABC) "
            "transporter superfamily. The MRP subfamily (ABCC subfamily) is "
            "composed of 13 members, of which MRP1 to MRP9 are the major "
            "transporters that cause multidrug resistance in tumor cells by pumping "
            "anticancer drugs out of the cell. These nine MRP members function as "
            "ATP-dependent exporters for endogenous substances and xenobiotics. MRP "
            "family can be divided into two groups, depending on their structural "
            "architecture. MRP4, MRP5, MRP8, and MRP9 (ABCC4, 5, 11 and 12, "
            "respectively) have a typical ABC transporter structure and each "
            "composed of two transmembrane domains (TMD1 and TMD2) and two "
            "nucleotide domains (NBD1 and NBD2). On the other hand, MRP1, 2, 3, 6 "
            "and 7 (ABCC1, 2, 3, 6 and 7, respectively) have an additional "
            "N-terminal five transmembrane segments in a single domain (TMD0) "
            "connected to the core (TMD-NBD) by a cytoplasmic linker (L0)"
        ),
        replacements=(
            (
                "The MRP subfamily (ABCC subfamily) is composed of 13 members, of "
                "which MRP1 to MRP9 are the major transporters that cause multidrug "
                "resistance in tumor cells by pumping anticancer drugs out of the "
                "cell. These nine MRP members function as ATP-dependent exporters "
                "for endogenous substances and xenobiotics.",
                "The human ABCC subfamily includes nine multidrug "
                "resistance-associated proteins (MRP1-MRP6 corresponding to "
                "ABCC1-ABCC6, and MRP7-MRP9 corresponding to ABCC10-ABCC12, whereas "
                "ABCC7 is the CFTR chloride channel and ABCC8/ABCC9 are the "
                "sulfonylurea receptors SUR1/SUR2). Several MRP members (notably "
                "MRP1-MRP5, MRP7/ABCC10, and MRP8/ABCC11) function as ATP-dependent "
                "efflux pumps for endogenous organic anions, cyclic nucleotides, and "
                "xenobiotics, whereas physiological substrates and transport "
                "activity of MRP9 (ABCC12) remain less characterized.",
            ),
            (
                "On the other hand, MRP1, 2, 3, 6 and 7 (ABCC1, 2, 3, 6 and 7, "
                "respectively)",
                "On the other hand, MRP1, 2, 3, 6 and 7 (ABCC1, 2, 3, 6 and 10, "
                "respectively)",
            ),
        ),
        definition_source=(
            "NCBI CDD; PTM source-definition erratum #1171 "
            "(Stage 4 finding F10; PMID:16984901; UniProtKB:Q96J65)"
        ),
        evidence=(
            (
                "PMID:16984901",
                "The human ABCC subfamily contains 12 full transporters, including nine MRPs (MRP1-6/ABCC1-6 and MRP7-9/ABCC10-12), CFTR (ABCC7), and SUR1/SUR2 (ABCC8/9)",
                "Deeley et al. (2006, Physiol Rev 86:849-899) and UniProtKB:Q96J65 "
                "(ABCC12/MRP9) establish that MRP7 is ABCC10 (whereas ABCC7 is the "
                "CFTR chloride channel) and that MRP9/ABCC12 has not been shown to "
                "act as a broad tumor multidrug resistance efflux pump.",
            ),
        ),
        event_action="source_erratum_cd18592",
        event_changes=(
            "Corrected the false mapping of MRP7 to ABCC7 (MRP7 is ABCC10; ABCC7 "
            "is CFTR) and qualified the overgeneralized claim that all MRP1-MRP9 "
            "members are characterized tumor multidrug resistance efflux pumps "
            "(#1171, Stage 4 finding F10)."
        ),
    ),
    "cd18593": CddErratum(
        accession="cd18593",
        finding_id="F18",
        label="ABC_6TM_MRP4_D1_like",
        parent="cl38913",
        rel_path=(
            "sequence/domain/cdd/"
            "six-transmembrane-helical-domain-1-tmd1-of-multidrug-resistance-associ-cd18593.yaml"
        ),
        source_description=(
            "Six-transmembrane helical domain 1 (TMD1) of multidrug "
            "resistance-associated protein 4 (MRP4) and similar proteins. This "
            "group represents the six-transmembrane domain 1 (TMD1) of multidrug "
            "resistance-associated protein 4 (MRP4), which belongs to the "
            "subfamily C of the ATP-binding cassette (ABC) transporter "
            "superfamily. The MRP subfamily (ABCC subfamily) is composed of 13 "
            "members, of which MRP1 to MRP9 are the major transporters that cause "
            "multidrug resistance in tumor cells by pumping anticancer drugs out "
            "of the cell. These nine MRP members function as ATP-dependent "
            "exporters for endogenous substances and xenobiotics. MRP family can "
            "be divided into two groups, depending on their structural "
            "architecture. MRP4, MRP5, MRP8, and MRP9 (ABCC4, 5, 11 and 12, "
            "respectively) have a typical ABC transporter structure and each "
            "composed of two transmembrane domains (TMD1 and TMD2) and two "
            "nucleotide domains (NBD1 and NBD2). On the other hand, MRP1, 2, 3, 6 "
            "and 7 (ABCC1, 2, 3, 6 and 7, respectively) have an additional "
            "N-terminal five transmembrane segments in a single domain (TMD0) "
            "connected to the core (TMD-NBD) by a cytoplasmic linker (L0)"
        ),
        replacements=(
            (
                "The MRP subfamily (ABCC subfamily) is composed of 13 members, of "
                "which MRP1 to MRP9 are the major transporters that cause multidrug "
                "resistance in tumor cells by pumping anticancer drugs out of the "
                "cell. These nine MRP members function as ATP-dependent exporters "
                "for endogenous substances and xenobiotics.",
                "The human ABCC subfamily includes nine multidrug "
                "resistance-associated proteins (MRP1-MRP6 corresponding to "
                "ABCC1-ABCC6, and MRP7-MRP9 corresponding to ABCC10-ABCC12, whereas "
                "ABCC7 is the CFTR chloride channel and ABCC8/ABCC9 are the "
                "sulfonylurea receptors SUR1/SUR2). Several MRP members (notably "
                "MRP1-MRP5, MRP7/ABCC10, and MRP8/ABCC11) function as ATP-dependent "
                "efflux pumps for endogenous organic anions, cyclic nucleotides, and "
                "xenobiotics, whereas physiological substrates and transport "
                "activity of MRP9 (ABCC12) remain less characterized.",
            ),
            (
                "On the other hand, MRP1, 2, 3, 6 and 7 (ABCC1, 2, 3, 6 and 7, "
                "respectively)",
                "On the other hand, MRP1, 2, 3, 6 and 7 (ABCC1, 2, 3, 6 and 10, "
                "respectively)",
            ),
        ),
        definition_source=(
            "NCBI CDD; PTM source-definition erratum #1188 "
            "(Cycle 2 Stage 4 finding F18; PMID:16984901; UniProtKB:O15439)"
        ),
        evidence=(
            (
                "PMID:16984901",
                "The human ABCC subfamily contains 12 full transporters, including nine MRPs (MRP1-6/ABCC1-6 and MRP7-9/ABCC10-12), CFTR (ABCC7), and SUR1/SUR2 (ABCC8/9)",
                "Deeley et al. (2006, Physiol Rev 86:849-899) and UniProtKB:O15439 "
                "(ABCC4/MRP4) establish that MRP7 is ABCC10 (whereas ABCC7 is the "
                "CFTR chloride channel) and that MRP9/ABCC12 has not been shown to "
                "act as a broad tumor multidrug resistance efflux pump.",
            ),
        ),
        event_action="source_erratum_cd18593",
        event_changes=(
            "Corrected the false mapping of MRP7 to ABCC7 (MRP7 is ABCC10; ABCC7 "
            "is CFTR) and qualified the overgeneralized claim that all MRP1-MRP9 "
            "members are characterized tumor multidrug resistance efflux pumps "
            "(#1188, Cycle 2 Stage 4 finding F18)."
        ),
        curation_timestamp=CYCLE2_CURATION_TIMESTAMP,
    ),
    "cd20534": CddErratum(
        accession="cd20534",
        finding_id="F11",
        label="CYCLIN_CCNM_CCNQ_rpt1",
        parent="cl40454",
        rel_path=(
            "sequence/domain/cdd/"
            "first-cyclin-box-found-in-cyclin-m-ccnm-family-the-ccnm-family-protein-cd20534.yaml"
        ),
        source_description=(
            "first cyclin box found in cyclin-M (CCNM) family. The CCNM family "
            "proteins, also called ancient conserved domain proteins (ACDPs), are "
            "evolutionarily conserved Mg2+ transporters. CCNM, also called cyclin-Q "
            "(CCNQ), or CDK10-activating cyclin, or cyclin-related protein FAM58A, "
            "associates with CDK10 to promote its kinase activity. Members of this "
            "family contain two cyclin boxes. This model corresponds to the first "
            "one. The cyclin box is a protein binding domain"
        ),
        replacements=(
            (
                "The CCNM family proteins, also called ancient conserved domain "
                "proteins (ACDPs), are evolutionarily conserved Mg2+ transporters. "
                "CCNM, also called cyclin-Q (CCNQ), or CDK10-activating cyclin, or "
                "cyclin-related protein FAM58A, associates with CDK10 to promote "
                "its kinase activity.",
                "Cyclin-M (CCNM), officially designated cyclin-Q (CCNQ, formerly "
                "FAM58A; distinct from the CNNM1-4/ACDP magnesium transporter "
                "family in CDD:cd04590), is the CDK10-activating cyclin that "
                "associates with CDK10 to promote its protein kinase activity.",
            ),
        ),
        definition_source=(
            "NCBI CDD; PTM source-definition erratum #1171 "
            "(Stage 4 finding F11; PMID:23912459; UniProtKB:Q8N1B3)"
        ),
        evidence=(
            (
                "PMID:23912459",
                "Cyclin M (FAM58A) interacts with CDK10 and forms an active protein kinase complex",
                "Guen et al. (2013, Nat Genet 45:1038-1042) and UniProtKB:Q8N1B3 "
                "(CCNQ/FAM58A, HGNC:28434) establish that cyclin-Q (formerly called "
                "cyclin-M/FAM58A) is the CDK10-activating cyclin containing two "
                "cyclin boxes, unrelated to the CNNM1-4 (ACDP1-4) ancient conserved "
                "domain magnesium transporter family (CDD:cd04590).",
            ),
        ),
        event_action="source_erratum_cd20534",
        event_changes=(
            "Removed the false conflation of the CDK10-activating cyclin "
            "CCNQ/FAM58A (informally called cyclin-M) with the unrelated "
            "CNNM1-4/ACDP magnesium transporter family (#1171, Stage 4 finding F11)."
        ),
    ),
    "cd20535": CddErratum(
        accession="cd20535",
        finding_id="F13",
        label="CYCLIN_CCNM_CCNQ_rpt2",
        parent="cl40454",
        rel_path=(
            "sequence/domain/cdd/"
            "second-cyclin-box-found-in-cyclin-m-ccnm-family-the-ccnm-family-protei-cd20535.yaml"
        ),
        source_description=(
            "second cyclin box found in cyclin-M (CCNM) family. The CCNM family "
            "proteins, also called ancient conserved domain proteins (ACDPs), are "
            "evolutionarily conserved Mg2+ transporters. CCNM, also called cyclin-Q "
            "(CCNQ), or CDK10-activating cyclin, or cyclin-related protein FAM58A, "
            "associates with CDK10 to promote its kinase activity. Members of this "
            "family contain two cyclin boxes. This model corresponds to the second "
            "one. The cyclin box is a protein binding domain"
        ),
        replacements=(
            (
                "The CCNM family proteins, also called ancient conserved domain "
                "proteins (ACDPs), are evolutionarily conserved Mg2+ transporters. "
                "CCNM, also called cyclin-Q (CCNQ), or CDK10-activating cyclin, or "
                "cyclin-related protein FAM58A, associates with CDK10 to promote "
                "its kinase activity.",
                "Cyclin-M (CCNM), officially designated cyclin-Q (CCNQ, formerly "
                "FAM58A; distinct from the CNNM1-4/ACDP magnesium transporter "
                "family in CDD:cd04590), is the CDK10-activating cyclin that "
                "associates with CDK10 to promote its protein kinase activity.",
            ),
        ),
        definition_source=(
            "NCBI CDD; PTM source-definition erratum #1188 "
            "(Cycle 2 Stage 4 finding F13; PMID:23912459; UniProtKB:Q8N1B3)"
        ),
        evidence=(
            (
                "PMID:23912459",
                "Cyclin M (FAM58A) interacts with CDK10 and forms an active protein kinase complex",
                "Guen et al. (2013, Nat Genet 45:1038-1042) and UniProtKB:Q8N1B3 "
                "(CCNQ/FAM58A, HGNC:28434) establish that cyclin-Q (formerly called "
                "cyclin-M/FAM58A) is the CDK10-activating cyclin containing two "
                "cyclin boxes, unrelated to the CNNM1-4 (ACDP1-4) ancient conserved "
                "domain magnesium transporter family (CDD:cd04590).",
            ),
        ),
        event_action="source_erratum_cd20535",
        event_changes=(
            "Removed the false conflation of the CDK10-activating cyclin "
            "CCNQ/FAM58A (informally called cyclin-M) with the unrelated "
            "CNNM1-4/ACDP magnesium transporter family (#1188, Cycle 2 Stage 4 "
            "finding F13)."
        ),
        curation_timestamp=CYCLE2_CURATION_TIMESTAMP,
    ),
    "cd21551": CddErratum(
        accession="cd21551",
        finding_id="F12",
        label="VEFS-box_SUZ12",
        parent="cl41782",
        rel_path=(
            "sequence/domain/cdd/"
            "vefs-vrn2-emf2-fis2-su-z-12-box-found-in-suppressor-of-zeste-12-protei-cd21551.yaml"
        ),
        source_description=(
            "VEFS (VRN2-EMF2-FIS2-Su(z)12) box found in suppressor of zeste 12 "
            "protein (SUZ12) and similar proteins. SUZ12, also called chromatin "
            "precipitated E2F target 9 protein (ChET 9 protein), or joined to "
            "JAZF1 protein, is a Polycomb group (PcG) protein that acts as a "
            "component of the PRC2/EED-EZH2 complex, which methylates 'Lys-9' "
            "(H3K9me) and 'Lys-27' (H3K27me) of histone H3, leading to "
            "transcriptional repression of the affected target gene. The "
            "PRC2/EED-EZH2 complex may also serve as a recruiting platform for DNA "
            "methyltransferases, thereby linking two epigenetic repression systems. "
            "This model corresponds to the VEFS (VRN2-EMF2-FIS2-Su(z)12) box at the "
            "C-terminus of SUZ12, which is responsible for binding to EED and EZH2"
        ),
        replacements=(
            (
                "which methylates 'Lys-9' (H3K9me) and 'Lys-27' (H3K27me) of "
                "histone H3, leading to transcriptional repression of the affected "
                "target gene.",
                "which methylates 'Lys-27' (H3K27me) of histone H3 to mediate "
                "transcriptional repression of target genes, while SUZ12 also "
                "influences H3K9 methylation indirectly through heterochromatin "
                "pathways.",
            ),
        ),
        definition_source=(
            "NCBI CDD; PTM source-definition erratum #1171 "
            "(Stage 4 finding F12; PMID:15225548; UniProtKB:Q15022)"
        ),
        evidence=(
            (
                "PMID:15225548",
                "SUZ12 is essential for the activity of the Polycomb repressive complex 2 (PRC2), which methylates lysine 27 of histone H3",
                "Pasini et al. (2004, EMBO J 23:4061-4071) and UniProtKB:Q15022 "
                "(SUZ12) establish that PRC2 (EZH2-EED-SUZ12) is a histone H3 "
                "Lys-27 (H3K27) methyltransferase complex rather than a direct "
                "H3K9 methyltransferase.",
            ),
        ),
        event_action="source_erratum_cd21551",
        event_changes=(
            "Corrected the statement that the PRC2/EED-EZH2 complex directly "
            "methylates both H3K9 and H3K27: PRC2 directly methylates H3K27 "
            "(H3K27me), while SUZ12 influences H3K9 methylation indirectly "
            "(#1171, Stage 4 finding F12)."
        ),
    ),
}


def correct_description(acc: str, description: str, parent: str) -> str:
    """Accept only the inspected CDD description (or its exact corrected form)."""
    erratum = ERRATA.get(acc)
    if erratum is None:
        return description
    if parent != erratum.parent:
        raise ValueError(f"{acc}: unexpected parent {parent!r}; re-review required")
    normalized = " ".join(description.split())
    if normalized not in {erratum.source_description, erratum.corrected_description}:
        raise ValueError(f"{acc}: source description drift; re-review required")
    return erratum.corrected_description


def metadata_blocks(acc: str) -> dict[str, str]:
    """Deterministic provenance blocks for a reviewed CDD erratum."""
    erratum = ERRATA[acc]
    evidence = "evidence:\n" + "".join(
        f"  - reference: {yaml_escape(reference)}\n"
        f"    snippet: {yaml_escape(snippet)}\n"
        f"    notes: {yaml_escape(notes)}\n"
        for reference, snippet, notes in erratum.evidence
    )
    return {
        "evidence": evidence,
        "curation_history": (
            f'curation_history:\n  - timestamp: "{erratum.curation_timestamp}"\n'
            "    curator: claude\n"
            f"    action: {erratum.event_action}\n"
            f"    changes: {yaml_escape(erratum.event_changes)}\n"
            "    llm_assisted: true\n"
        ),
    }
