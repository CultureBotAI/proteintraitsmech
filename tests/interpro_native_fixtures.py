"""Small synthetic API objects: real grouping shapes, invented protein sequences."""

import hashlib


def synthetic_canaries():
    result = {}
    for acc, taxon, length in (("P05719", 83333, 464), ("Q796K8", 12345, 400)):
        sequence = "M" + "C" * (length - 1)
        reference = {
            "protein_id": f"UniProtKB:{acc}", "protein_label": "Synthetic test protein",
            "taxon_id": f"NCBITaxon:{taxon}", "taxon_label": "Synthetic test organism",
            "sequence": sequence, "sequence_length": length,
            "sequence_sha256": hashlib.sha256(sequence.encode()).hexdigest(),
            "sequence_version": 1, "reviewed": True, "uniprot_release": "2026_03",
        }

        def location(fragments):
            return {"fragments": [{"start": a, "end": b, "dc-status": status}
                                  for a, b, status in fragments],
                    "representative": False, "model": "synthetic"}

        if acc == "P05719":
            definitions = [("interpro", "IPR000055", [
                location([(7, 190, "CONTINUOUS")]),
                location([(348, 403, "CONTINUOUS")])])]
            definitions += [("pfam", f"PF{i:05d}", [location([(10, 40, "CONTINUOUS")])])
                            for i in range(1, 10)]
        else:
            definitions = [
                ("cathgene3d", "G3DSA:1.10.10.1230", [location([(86, 202, "CONTINUOUS")])]),
                ("ssf", "SSF56519", [location([(59, 121, "C_TERMINAL_DISC"),
                                               (212, 341, "N_TERMINAL_DISC")])]),
                ("interpro", "IPR036138", [location([(59, 341, "CONTINUOUS")])]),
            ]
        entries = [{"metadata": {"source_database": db, "accession": identifier},
                    "proteins": [{"accession": acc, "protein_length": length,
                                  "organism": taxon, "source_database": "reviewed",
                                  "entry_protein_locations": locations}]}
                   for db, identifier, locations in definitions]
        result[acc] = (
            {"count": len(entries), "next": None, "previous": None, "results": entries},
            {"metadata": {"accession": acc, "sequence": sequence, "length": length,
                          "source_organism": {"taxId": taxon}, "source_database": "reviewed",
                          "counters": {"entries": len(entries)}}},
            reference,
        )
    return result
