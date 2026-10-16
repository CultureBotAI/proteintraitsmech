"""Accession-scoped, evidence-backed Complex Portal source errata.

Shared by the seeder and guarded repair; this is not a global prose replacement.
CPX-2267's inspected source function is pinned in the 20261013 scientific review:
https://www.ebi.ac.uk/intact/complex-ws/complex/CPX-2267
JSON SHA-256: e264491510c1bc2d750f24322a21016dffff55bfdb2488e002d0fa09b7045f31
Only reaction products are corrected (#1114). Unexpected upstream wording must
be re-reviewed, not silently overwritten. No protein qualification is conferred.
"""

from __future__ import annotations

from yaml_emit import yaml_escape

ACCESSION = "CPX-2267"
IDENTIFIER = f"ComplexPortal:{ACCESSION}"
MEMBERS = {"UniProtKB:P00445", "UniProtKB:P40202"}
SOURCE_DESCRIPTION = (
    "Complex formation results in the activationof the antioxidant enzyme copper, zinc "
    "superoxide dismutase,SOD1 which protects cells against oxygen stress and reactive "
    "oxygen species by converting superoxide radicals into water and hydrogen peroxide. "
    "SOD1 (CPX-2896) activation involves insertion of copper and oxidation of an "
    "intrasubunit disulfide bond. Insertion of copper is required for any enzymatic "
    "activity. Oxidation of the disulfide bond is required to increase the enzymatic "
    "activity from approximately 10 % in disulfide-reduced SOD1 to 100 % in "
    "disulfide-oxidized SOD1. The copper chaperone, CCS1 (CPX-2895), both delivers "
    "the copper and oxidises the disulfide bond."
)
CORRECTED_DESCRIPTION = SOURCE_DESCRIPTION.replace(
    "water and hydrogen peroxide", "oxygen and hydrogen peroxide"
)
DEFINITION_SOURCE = (
    "Complex Portal; PTM reaction-product erratum #1114 "
    "(https://enzyme.expasy.org/EC/1.15.1.1)"
)
EVIDENCE = (
    (
        "https://enzyme.expasy.org/EC/1.15.1.1",
        "2 superoxide + 2 H(+) = H2O2 + O2",
        "Database reaction assertion inspected 2026-10-14. Corrects only the "
        "SOD1 reaction products in the definition: oxygen and hydrogen peroxide, "
        "not water. Does not establish activity of the SOD1-CCS1 heterodimer or "
        "independently verify the inherited activation percentages.",
    ),
    (
        "DOI:10.1038/nsb0901-751",
        "a complex comprising one monomer of each protein",
        "Primary-study abstract inspected via https://www.rcsb.org/structure/1JK9 "
        "on 2026-10-14 (PMID:11524675). The structure uses yeast H48F-SOD1 and "
        "yeast CCS. Supports heterodimeric association in the maturation context, "
        "not equivalence to mature SOD1 homodimer CPX-2896, wild-type catalytic "
        "activity, or a new qualified protein example.",
    ),
)
EVENT_ACTION = "source_erratum_cpx_2267"
EVENT_CHANGES = (
    "Corrected water to oxygen in the SOD1 reaction products using EC 1.15.1.1 "
    "(#1114); retained the source activation description, identity and membership. "
    "Added claim-scoped evidence and the H48F structural-context limitation. "
    "No canonical example or residue-level claim promoted; independent review pending."
)


def correct_description(ac: str, description: str, members: list[str],
                        subparts: list[str]) -> str:
    """Accept only the inspected description (or its exact corrected form)."""
    if ac != ACCESSION:
        return description
    if len(members) != 2 or set(members) != MEMBERS or subparts:
        raise ValueError(f"{ACCESSION}: unexpected membership; re-review required")
    normalized = " ".join(description.split())
    if normalized not in {SOURCE_DESCRIPTION, CORRECTED_DESCRIPTION}:
        raise ValueError(f"{ACCESSION}: source description drift; re-review required")
    return CORRECTED_DESCRIPTION


def metadata_blocks() -> dict[str, str]:
    """Deterministic provenance: event date is the erratum's, not each reseed's."""
    evidence = "evidence:\n" + "".join(
        f"  - reference: {yaml_escape(reference)}\n"
        f"    snippet: {yaml_escape(snippet)}\n"
        f"    notes: {yaml_escape(notes)}\n"
        for reference, snippet, notes in EVIDENCE
    )
    return {
        "evidence": evidence,
        "curation_history": (
            'curation_history:\n  - timestamp: "2026-10-14T19:44:39Z"\n'
            "    curator: claude\n"
            f"    action: {EVENT_ACTION}\n"
            f"    changes: {yaml_escape(EVENT_CHANGES)}\n"
            "    llm_assisted: true\n"
        ),
    }
