#!/usr/bin/env python3
"""Rewrite ADC class C beta-lactamase ARO causal graphs.

The ADC subgroup and leaf records already have the right class C serine
beta-lactamase graph shape, but each mechanistic edge carries only one
literature reference and most edges have no description. This updater rewrites
the exact rank-77 ADC records with fully described, multi-evidence class C
graphs while preserving every existing determinant-to-drug-class edge.

Dry-run by default; pass ``--apply`` to write.
"""

from __future__ import annotations

import argparse
import copy
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from record_io import append_to_section, replace_block  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ARO_DIR = ROOT / "data" / "traits" / "function" / "resistance" / "aro"

HISTORY_CURATOR = "codex-causal-graph-quality"
HISTORY_EVENT = {
    "timestamp": "2026-09-08T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": "Completed ADC class C beta-lactamase causal graphs",
    "llm_assisted": True,
}

INACTIVATION_ENZYME_EVIDENCE = {
    "reference": "ARO:3000557",
    "snippet": (
        "Enzyme that catalyzes the inactivation of an antibiotic resulting in "
        "resistance."
    ),
    "notes": "CARD definition for antibiotic inactivation enzymes.",
}

ANTIBIOTIC_INACTIVATION_EVIDENCE = {
    "reference": "ARO:0001004",
    "snippet": "Enzymatic inactivation of antibiotic to confer drug resistance.",
    "notes": "CARD definition for antibiotic inactivation.",
}

BETA_LACTAMASE_EVIDENCE = {
    "reference": "ARO:3000001",
    "snippet": (
        "The lactamase enzyme breaks that ring open, deactivating the "
        "molecule's antibacterial properties."
    ),
    "notes": "CARD definition for beta-lactamases.",
}

ADC_EVIDENCE = {
    "reference": "ARO:3005459",
    "snippet": (
        "ADC beta-lactamases, also known as AmpC beta-lactamases, are "
        "cephalosporinases with extended-spectrum resistance to cephalosporins "
        "and may or may not cause resistance to carbapenems. ADC "
        "beta-lactamases are found in Acinetobacter sp. and Oligella "
        "urethralis."
    ),
    "notes": "CARD definition for ADC beta-lactamase.",
}

CLASS_C_EVIDENCE = {
    "reference": "ARO:3000076",
    "snippet": (
        "AmpC type beta-lactamases are commonly isolated from "
        "extended-spectrum cephalosporin-resistant Gram-negative bacteria. "
        "AmpC beta-lactamases (also termed class C or group 1) are typically "
        "encoded on the chromosome of many Gram-negative bacteria including "
        "Citrobacter, Serratia, Enterobacter species, and P. aeruginosa where "
        "its expression is usually inducible; it may also occur on "
        "Escherichia coli but is not usually inducible, although it can be "
        "hyperexpressed. AmpC type beta-lactamases may also be carried on "
        "plasmids. AmpC beta-lactamases, in contrast to ESBLs, hydrolyse "
        "broad and extended-spectrum cephalosporins (cephamycins as well as "
        "to oxyimino-beta-lactams) but are not inhibited by beta-lactamase "
        "inhibitors such as clavulanic acid."
    ),
    "notes": "CARD definition for class C beta-lactamase.",
}

SERINE_BETA_LACTAMASE_EVIDENCE = {
    "reference": "ARO:3000187",
    "snippet": (
        "Mechanism of enzymatic degradation common to Ambler Class A, C and D "
        "beta-lactamases. A serine residue located in the active site is used "
        "to form an acyl-enzyme intermediate and subsequent hydrolysis renders "
        "the beta-lactam inactive."
    ),
    "notes": "CARD definition for serine beta-lactamase hydrolysis.",
}

AMPC_REACTION_EVIDENCE = {
    "reference": "PMID:19136439",
    "snippet": (
        "AmpC β-lactamases are clinically important cephalosporinases encoded "
        "on the chromosomes of many of the Enterobacteriaceae and a few other "
        "organisms."
    ),
    "notes": "Evidence for AmpC/class C beta-lactamases.",
}

PROSITE_EVIDENCE = {
    "reference": "PROSITE:PRU10102",
    "snippet": "Beta-lactamase class-C active site",
    "notes": "PROSITE active-site signature for class C beta-lactamases.",
}

CATH_EVIDENCE = {
    "reference": "CATH:3.40.710.10",
    "snippet": "DD-peptidase/beta-lactamase superfamily",
    "notes": "CATH fold for serine beta-lactamases.",
}

MECH0_NODE = {
    "node_id": "mech0",
    "label": "antibiotic inactivation",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:0001004",
}

MECH1_NODE = {
    "node_id": "mech1",
    "label": "hydrolysis of beta-lactam antibiotic by serine beta-lactamase",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000187",
}

ACTIVE_SITE_NODE = {
    "node_id": "active_site",
    "label": "class C beta-lactamase active-site signature (Ser64 S-x-x-K)",
    "node_type": "MOTIF",
    "grounding": "PROSITE:PRU10102",
    "description": "Class C beta-lactamase catalytic serine active-site signature.",
}

FOLD_NODE = {
    "node_id": "fold",
    "label": "DD-peptidase/beta-lactamase superfamily fold",
    "node_type": "DOMAIN",
    "grounding": "CATH:3.40.710.10",
    "description": "DD-peptidase/beta-lactamase superfamily fold.",
}

RESISTANCE_NODE = {
    "node_id": "resistance",
    "label": "antibiotic resistance phenotype",
    "node_type": "PHENOTYPE",
    "grounding": "GO:0046677",
    "description": (
        "Resistance phenotype conferred by this determinant. Grounded to the "
        "nearest available superclass: ARO models determinants and mechanisms "
        "but has no term for the resistance phenotype itself."
    ),
}

CORE_EDGE_KEYS = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0000056", "mech1"),
    ("mech1", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("active_site", "BFO:0000050", "determinant"),
    ("determinant", "RO:0002350", "fold"),
    ("active_site", "RO:0002327", "mech1"),
}

DRUG_ID = re.compile(r"^drug\d+$")


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str


_TARGET_ROWS = """
ARO:3003847 adc-1-aro3003847.yaml
ARO:3003855 adc-10-aro3003855.yaml
ARO:3006280 adc-100-aro3006280.yaml
ARO:3006281 adc-101-aro3006281.yaml
ARO:3006282 adc-102-aro3006282.yaml
ARO:3006283 adc-103-aro3006283.yaml
ARO:3006284 adc-104-aro3006284.yaml
ARO:3006285 adc-105-aro3006285.yaml
ARO:3006286 adc-106-aro3006286.yaml
ARO:3006287 adc-107-aro3006287.yaml
ARO:3006288 adc-109-aro3006288.yaml
ARO:3004615 adc-11-aro3004615.yaml
ARO:3006289 adc-110-aro3006289.yaml
ARO:3006290 adc-112-aro3006290.yaml
ARO:3006291 adc-113-aro3006291.yaml
ARO:3006292 adc-114-aro3006292.yaml
ARO:3006293 adc-115-aro3006293.yaml
ARO:3006294 adc-116-aro3006294.yaml
ARO:3006295 adc-117-aro3006295.yaml
ARO:3006296 adc-119-aro3006296.yaml
ARO:3003856 adc-12-aro3003856.yaml
ARO:3006297 adc-120-aro3006297.yaml
ARO:3006298 adc-121-aro3006298.yaml
ARO:3006299 adc-122-aro3006299.yaml
ARO:3006300 adc-123-aro3006300.yaml
ARO:3006301 adc-125-aro3006301.yaml
ARO:3006302 adc-127-aro3006302.yaml
ARO:3006303 adc-128-aro3006303.yaml
ARO:3006304 adc-129-aro3006304.yaml
ARO:3003857 adc-13-aro3003857.yaml
ARO:3006305 adc-130-aro3006305.yaml
ARO:3006306 adc-131-aro3006306.yaml
ARO:3006307 adc-132-aro3006307.yaml
ARO:3006308 adc-133-aro3006308.yaml
ARO:3006309 adc-134-aro3006309.yaml
ARO:3006310 adc-135-aro3006310.yaml
ARO:3006311 adc-136-aro3006311.yaml
ARO:3006312 adc-137-aro3006312.yaml
ARO:3006313 adc-138-aro3006313.yaml
ARO:3006314 adc-139-aro3006314.yaml
ARO:3003858 adc-14-aro3003858.yaml
ARO:3006315 adc-140-aro3006315.yaml
ARO:3006316 adc-141-aro3006316.yaml
ARO:3006317 adc-143-aro3006317.yaml
ARO:3006318 adc-144-aro3006318.yaml
ARO:3006319 adc-145-aro3006319.yaml
ARO:3006320 adc-146-aro3006320.yaml
ARO:3006321 adc-147-aro3006321.yaml
ARO:3006322 adc-148-aro3006322.yaml
ARO:3006323 adc-149-aro3006323.yaml
ARO:3003859 adc-15-aro3003859.yaml
ARO:3006324 adc-150-aro3006324.yaml
ARO:3006325 adc-151-aro3006325.yaml
ARO:3006326 adc-152-aro3006326.yaml
ARO:3006327 adc-153-aro3006327.yaml
ARO:3006328 adc-154-aro3006328.yaml
ARO:3006329 adc-155-aro3006329.yaml
ARO:3006330 adc-156-aro3006330.yaml
ARO:3006331 adc-157-aro3006331.yaml
ARO:3006332 adc-158-aro3006332.yaml
ARO:3005037 adc-159-aro3005037.yaml
ARO:3003860 adc-16-aro3003860.yaml
ARO:3006333 adc-160-aro3006333.yaml
ARO:3006334 adc-162-aro3006334.yaml
ARO:3006335 adc-163-aro3006335.yaml
ARO:3006336 adc-164-aro3006336.yaml
ARO:3006337 adc-165-aro3006337.yaml
ARO:3006338 adc-166-aro3006338.yaml
ARO:3006339 adc-167-aro3006339.yaml
ARO:3006340 adc-168-aro3006340.yaml
ARO:3006341 adc-169-aro3006341.yaml
ARO:3003861 adc-17-aro3003861.yaml
ARO:3006342 adc-170-aro3006342.yaml
ARO:3006343 adc-171-aro3006343.yaml
ARO:3006344 adc-172-aro3006344.yaml
ARO:3006345 adc-173-aro3006345.yaml
ARO:3006346 adc-174-aro3006346.yaml
ARO:3006347 adc-175-aro3006347.yaml
ARO:3006348 adc-176-aro3006348.yaml
ARO:3006349 adc-177-aro3006349.yaml
ARO:3006350 adc-178-aro3006350.yaml
ARO:3006351 adc-179-aro3006351.yaml
ARO:3003862 adc-18-aro3003862.yaml
ARO:3006352 adc-180-aro3006352.yaml
ARO:3005244 adc-181-aro3005244.yaml
ARO:3005245 adc-182-aro3005245.yaml
ARO:3005246 adc-183-aro3005246.yaml
ARO:3006353 adc-184-aro3006353.yaml
ARO:3006354 adc-185-aro3006354.yaml
ARO:3006355 adc-186-aro3006355.yaml
ARO:3006356 adc-187-aro3006356.yaml
ARO:3006357 adc-188-aro3006357.yaml
ARO:3006358 adc-189-aro3006358.yaml
ARO:3003863 adc-19-aro3003863.yaml
ARO:3006359 adc-190-aro3006359.yaml
ARO:3006360 adc-191-aro3006360.yaml
ARO:3006361 adc-192-aro3006361.yaml
ARO:3006362 adc-193-aro3006362.yaml
ARO:3006363 adc-194-aro3006363.yaml
ARO:3006364 adc-195-aro3006364.yaml
ARO:3006365 adc-196-aro3006365.yaml
ARO:3006366 adc-197-aro3006366.yaml
ARO:3006367 adc-198-aro3006367.yaml
ARO:3006368 adc-199-aro3006368.yaml
ARO:3003848 adc-2-aro3003848.yaml
ARO:3003864 adc-20-aro3003864.yaml
ARO:3006369 adc-200-aro3006369.yaml
ARO:3006370 adc-201-aro3006370.yaml
ARO:3006371 adc-202-aro3006371.yaml
ARO:3006372 adc-203-aro3006372.yaml
ARO:3006373 adc-204-aro3006373.yaml
ARO:3006374 adc-205-aro3006374.yaml
ARO:3006375 adc-206-aro3006375.yaml
ARO:3006376 adc-207-aro3006376.yaml
ARO:3006377 adc-208-aro3006377.yaml
ARO:3006378 adc-209-aro3006378.yaml
ARO:3003865 adc-21-aro3003865.yaml
ARO:3006379 adc-210-aro3006379.yaml
ARO:3006380 adc-211-aro3006380.yaml
ARO:3006381 adc-212-aro3006381.yaml
ARO:3006382 adc-213-aro3006382.yaml
ARO:3006383 adc-214-aro3006383.yaml
ARO:3006384 adc-215-aro3006384.yaml
ARO:3006385 adc-216-aro3006385.yaml
ARO:3006386 adc-217-aro3006386.yaml
ARO:3006387 adc-218-aro3006387.yaml
ARO:3006388 adc-219-aro3006388.yaml
ARO:3003866 adc-22-aro3003866.yaml
ARO:3006389 adc-220-aro3006389.yaml
ARO:3006390 adc-221-aro3006390.yaml
ARO:3006391 adc-222-aro3006391.yaml
ARO:3006392 adc-223-aro3006392.yaml
ARO:3006393 adc-224-aro3006393.yaml
ARO:3006394 adc-225-aro3006394.yaml
ARO:3006395 adc-226-aro3006395.yaml
ARO:3006396 adc-227-aro3006396.yaml
ARO:3006397 adc-228-aro3006397.yaml
ARO:3006398 adc-229-aro3006398.yaml
ARO:3003867 adc-23-aro3003867.yaml
ARO:3006399 adc-230-aro3006399.yaml
ARO:3006400 adc-231-aro3006400.yaml
ARO:3006401 adc-232-aro3006401.yaml
ARO:3006402 adc-233-aro3006402.yaml
ARO:3006403 adc-234-aro3006403.yaml
ARO:3006404 adc-235-aro3006404.yaml
ARO:3006405 adc-236-aro3006405.yaml
ARO:3006406 adc-237-aro3006406.yaml
ARO:3006407 adc-238-aro3006407.yaml
ARO:3006408 adc-239-aro3006408.yaml
ARO:3006409 adc-24-aro3006409.yaml
ARO:3006410 adc-240-aro3006410.yaml
ARO:3006411 adc-241-aro3006411.yaml
ARO:3006412 adc-242-aro3006412.yaml
ARO:3006413 adc-243-aro3006413.yaml
ARO:3006414 adc-244-aro3006414.yaml
ARO:3006415 adc-245-aro3006415.yaml
ARO:3006416 adc-246-aro3006416.yaml
ARO:3006417 adc-247-aro3006417.yaml
ARO:3006418 adc-248-aro3006418.yaml
ARO:3006419 adc-249-aro3006419.yaml
ARO:3003868 adc-25-aro3003868.yaml
ARO:3006420 adc-250-aro3006420.yaml
ARO:3006421 adc-251-aro3006421.yaml
ARO:3006422 adc-252-aro3006422.yaml
ARO:3006423 adc-253-aro3006423.yaml
ARO:3006424 adc-254-aro3006424.yaml
ARO:3006425 adc-255-aro3006425.yaml
ARO:3006426 adc-256-aro3006426.yaml
ARO:3007973 adc-257-aro3007973.yaml
ARO:3007974 adc-258-aro3007974.yaml
ARO:3007975 adc-259-aro3007975.yaml
ARO:3007976 adc-260-aro3007976.yaml
ARO:3007977 adc-261-aro3007977.yaml
ARO:3007978 adc-262-aro3007978.yaml
ARO:3007979 adc-263-aro3007979.yaml
ARO:3007980 adc-264-aro3007980.yaml
ARO:3007981 adc-265-aro3007981.yaml
ARO:3007982 adc-266-aro3007982.yaml
ARO:3007983 adc-267-aro3007983.yaml
ARO:3007984 adc-268-aro3007984.yaml
ARO:3007985 adc-269-aro3007985.yaml
ARO:3007986 adc-270-aro3007986.yaml
ARO:3007987 adc-271-aro3007987.yaml
ARO:3007988 adc-272-aro3007988.yaml
ARO:3007989 adc-273-aro3007989.yaml
ARO:3007990 adc-274-aro3007990.yaml
ARO:3007991 adc-275-aro3007991.yaml
ARO:3007992 adc-276-aro3007992.yaml
ARO:3007993 adc-277-aro3007993.yaml
ARO:3007994 adc-278-aro3007994.yaml
ARO:3007995 adc-279-aro3007995.yaml
ARO:3007996 adc-280-aro3007996.yaml
ARO:3007997 adc-281-aro3007997.yaml
ARO:3007998 adc-282-aro3007998.yaml
ARO:3007999 adc-283-aro3007999.yaml
ARO:3008000 adc-284-aro3008000.yaml
ARO:3008001 adc-285-aro3008001.yaml
ARO:3008002 adc-286-aro3008002.yaml
ARO:3008003 adc-287-aro3008003.yaml
ARO:3008004 adc-288-aro3008004.yaml
ARO:3008005 adc-289-aro3008005.yaml
ARO:3006427 adc-29-aro3006427.yaml
ARO:3008006 adc-290-aro3008006.yaml
ARO:3008007 adc-291-aro3008007.yaml
ARO:3008008 adc-292-aro3008008.yaml
ARO:3008009 adc-293-aro3008009.yaml
ARO:3008010 adc-294-aro3008010.yaml
ARO:3008011 adc-295-aro3008011.yaml
ARO:3003849 adc-3-aro3003849.yaml
ARO:3004617 adc-30-aro3004617.yaml
ARO:3008012 adc-302-aro3008012.yaml
ARO:3008013 adc-303-aro3008013.yaml
ARO:3008014 adc-304-aro3008014.yaml
ARO:3008015 adc-305-aro3008015.yaml
ARO:3008016 adc-306-aro3008016.yaml
ARO:3008017 adc-307-aro3008017.yaml
ARO:3008018 adc-308-aro3008018.yaml
ARO:3008019 adc-309-aro3008019.yaml
ARO:3003870 adc-31-aro3003870.yaml
ARO:3008020 adc-310-aro3008020.yaml
ARO:3008021 adc-311-aro3008021.yaml
ARO:3008022 adc-312-aro3008022.yaml
ARO:3008023 adc-313-aro3008023.yaml
ARO:3008024 adc-314-aro3008024.yaml
ARO:3008025 adc-315-aro3008025.yaml
ARO:3008026 adc-316-aro3008026.yaml
ARO:3008027 adc-317-aro3008027.yaml
ARO:3008028 adc-318-aro3008028.yaml
ARO:3008029 adc-319-aro3008029.yaml
ARO:3006428 adc-32-aro3006428.yaml
ARO:3008030 adc-320-aro3008030.yaml
ARO:3008031 adc-321-aro3008031.yaml
ARO:3008032 adc-322-aro3008032.yaml
ARO:3008033 adc-323-aro3008033.yaml
ARO:3008034 adc-324-aro3008034.yaml
ARO:3008035 adc-325-aro3008035.yaml
ARO:3008036 adc-326-aro3008036.yaml
ARO:3008037 adc-327-aro3008037.yaml
ARO:3008038 adc-328-aro3008038.yaml
ARO:3008039 adc-329-aro3008039.yaml
ARO:3006429 adc-33-aro3006429.yaml
ARO:3008040 adc-330-aro3008040.yaml
ARO:3008041 adc-331-aro3008041.yaml
ARO:3008042 adc-332-aro3008042.yaml
ARO:3008043 adc-333-aro3008043.yaml
ARO:3008044 adc-334-aro3008044.yaml
ARO:3008045 adc-335-aro3008045.yaml
ARO:3008046 adc-336-aro3008046.yaml
ARO:3008047 adc-337-aro3008047.yaml
ARO:3008048 adc-338-aro3008048.yaml
ARO:3008049 adc-339-aro3008049.yaml
ARO:3008050 adc-340-aro3008050.yaml
ARO:3008051 adc-341-aro3008051.yaml
ARO:3008052 adc-342-aro3008052.yaml
ARO:3008053 adc-343-aro3008053.yaml
ARO:3008054 adc-344-aro3008054.yaml
ARO:3008055 adc-345-aro3008055.yaml
ARO:3008056 adc-346-aro3008056.yaml
ARO:3008057 adc-347-aro3008057.yaml
ARO:3008058 adc-348-aro3008058.yaml
ARO:3008059 adc-349-aro3008059.yaml
ARO:3008060 adc-350-aro3008060.yaml
ARO:3008061 adc-351-aro3008061.yaml
ARO:3008062 adc-352-aro3008062.yaml
ARO:3008063 adc-353-aro3008063.yaml
ARO:3008064 adc-354-aro3008064.yaml
ARO:3008065 adc-355-aro3008065.yaml
ARO:3008066 adc-356-aro3008066.yaml
ARO:3008067 adc-357-aro3008067.yaml
ARO:3008068 adc-358-aro3008068.yaml
ARO:3008069 adc-359-aro3008069.yaml
ARO:3006430 adc-38-aro3006430.yaml
ARO:3003871 adc-39-aro3003871.yaml
ARO:3003850 adc-4-aro3003850.yaml
ARO:3003872 adc-41-aro3003872.yaml
ARO:3003873 adc-42-aro3003873.yaml
ARO:3003874 adc-43-aro3003874.yaml
ARO:3003876 adc-44-aro3003876.yaml
ARO:3003851 adc-5-aro3003851.yaml
ARO:3006431 adc-51-aro3006431.yaml
ARO:3006432 adc-52-aro3006432.yaml
ARO:3006433 adc-53-aro3006433.yaml
ARO:3006434 adc-54-aro3006434.yaml
ARO:3003878 adc-56-aro3003878.yaml
ARO:3006435 adc-57-aro3006435.yaml
ARO:3004618 adc-58-aro3004618.yaml
ARO:3004619 adc-59-aro3004619.yaml
ARO:3003852 adc-6-aro3003852.yaml
ARO:3004620 adc-60-aro3004620.yaml
ARO:3003879 adc-61-aro3003879.yaml
ARO:3004632 adc-62-aro3004632.yaml
ARO:3006436 adc-63-aro3006436.yaml
ARO:3006437 adc-65-aro3006437.yaml
ARO:3006438 adc-66-aro3006438.yaml
ARO:3004633 adc-67-aro3004633.yaml
ARO:3004493 adc-68-aro3004493.yaml
ARO:3003853 adc-7-aro3003853.yaml
ARO:3006439 adc-70-aro3006439.yaml
ARO:3004634 adc-73-aro3004634.yaml
ARO:3003880 adc-74-aro3003880.yaml
ARO:3003881 adc-75-aro3003881.yaml
ARO:3003882 adc-76-aro3003882.yaml
ARO:3003883 adc-77-aro3003883.yaml
ARO:3003884 adc-78-aro3003884.yaml
ARO:3003885 adc-79-aro3003885.yaml
ARO:3003854 adc-8-aro3003854.yaml
ARO:3003886 adc-80-aro3003886.yaml
ARO:3003887 adc-81-aro3003887.yaml
ARO:3003888 adc-82-aro3003888.yaml
ARO:3006440 adc-83-aro3006440.yaml
ARO:3006441 adc-84-aro3006441.yaml
ARO:3006442 adc-85-aro3006442.yaml
ARO:3006443 adc-86-aro3006443.yaml
ARO:3006444 adc-87-aro3006444.yaml
ARO:3006445 adc-88-aro3006445.yaml
ARO:3006446 adc-89-aro3006446.yaml
ARO:3006447 adc-90-aro3006447.yaml
ARO:3006448 adc-91-aro3006448.yaml
ARO:3006449 adc-92-aro3006449.yaml
ARO:3006450 adc-93-aro3006450.yaml
ARO:3006451 adc-94-aro3006451.yaml
ARO:3006452 adc-95-aro3006452.yaml
ARO:3006453 adc-96-aro3006453.yaml
ARO:3006454 adc-97-aro3006454.yaml
ARO:3006455 adc-98-aro3006455.yaml
ARO:3006456 adc-99-aro3006456.yaml
ARO:3004545 adc-beta-lactamase-with-carbapenemase-activity-aro3004545.yaml
ARO:3003846 adc-beta-lactamase-without-carbapenemase-activity-aro3003846.yaml
ARO:3005460 adc-beta-lactamases-pending-classification-for-carbapenemase-activity-aro3005460.yaml
"""

TARGETS: tuple[Target, ...] = tuple(
    Target(identifier, filename)
    for identifier, filename in (line.split() for line in _TARGET_ROWS.strip().splitlines())
)
TARGET_BY_ID = {target.identifier: target for target in TARGETS}


def _dump(obj: Any) -> str:
    return yaml.safe_dump(
        obj,
        sort_keys=False,
        allow_unicode=True,
        width=100,
        default_flow_style=False,
    )


def _dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _edge_key(edge: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(edge.get("subject", "")),
        str(edge.get("predicate_id", "")),
        str(edge.get("object", "")),
    )


def _is_drug_node_id(node_id: str) -> bool:
    return DRUG_ID.fullmatch(node_id) is not None


def _drug_sort_key(node: dict[str, Any]) -> int:
    match = DRUG_ID.fullmatch(str(node["node_id"]))
    if match is None:
        raise ValueError(f"unexpected drug node_id: {node['node_id']}")
    return int(str(node["node_id"])[len("drug") :])


def _unique_evidence(*items: dict[str, Any]) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for item in items:
        key = (str(item["reference"]), str(item.get("snippet", "")))
        if key in seen:
            continue
        seen.add(key)
        evidence.append(copy.deepcopy(item))
    return evidence


def _edge(
    subject: str,
    predicate: str,
    predicate_id: str,
    object_: str,
    description: str,
    *evidence: dict[str, Any],
) -> dict[str, Any]:
    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "description": description,
        "evidence": _unique_evidence(*evidence),
    }


def _record_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


def _determinant_node(record: dict[str, Any]) -> dict[str, str]:
    return {
        "node_id": "determinant",
        "label": str(record["label"]),
        "node_type": "PROTEIN",
        "grounding": str(record["identifier"]),
    }


def _nodes_by_id(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(node["node_id"]): node
        for node in _dicts(graph.get("nodes"))
        if "node_id" in node
    }


def _drug_nodes(graph: dict[str, Any]) -> list[dict[str, Any]]:
    drug_nodes = [
        node
        for node in _dicts(graph.get("nodes"))
        if _is_drug_node_id(str(node.get("node_id", "")))
    ]
    if not drug_nodes:
        raise ValueError("missing drug node")
    return [copy.deepcopy(node) for node in sorted(drug_nodes, key=_drug_sort_key)]


def _drug_relation_evidence(graph: dict[str, Any], drug_node_ids: set[str]) -> dict[str, list[dict]]:
    by_object: dict[str, list[dict]] = {node_id: [] for node_id in drug_node_ids}
    for edge in _dicts(graph.get("edges")):
        if (
            edge.get("subject") == "determinant"
            and edge.get("predicate_id") == "ARO:2000001"
        ):
            object_ = str(edge.get("object", ""))
            if object_ in by_object:
                by_object[object_].extend(
                    item
                    for item in _dicts(edge.get("evidence"))
                    if str(item.get("snippet", "")).startswith(
                        "relationship: confers_resistance_to_drug_class "
                    )
                )
    return by_object


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    nodes = _nodes_by_id(graph)
    drug_node_ids = {node_id for node_id in nodes if _is_drug_node_id(node_id)}
    required_nodes = {"determinant", "mech0", "mech1", "active_site", "fold", "resistance"}
    missing_nodes = sorted(required_nodes - set(nodes))
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")
    if not drug_node_ids:
        raise ValueError(f"{target.identifier}: missing drug node(s)")

    seen: set[tuple[str, str, str]] = set()
    found: set[tuple[str, str, str]] = set()
    direct_drug_edges: set[str] = set()
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        subject, predicate_id, object_ = key
        direct_drug_edge = (
            subject == "determinant"
            and predicate_id == "ARO:2000001"
            and object_ in drug_node_ids
        )
        if key not in CORE_EDGE_KEYS and not direct_drug_edge:
            raise ValueError(f"{target.identifier}: unexpected edge {subject} -> {object_}")
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {subject} -> {object_}")
        seen.add(key)
        found.add(key)
        if direct_drug_edge:
            direct_drug_edges.add(object_)

    missing_edges = sorted(CORE_EDGE_KEYS - found)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_edges)
        raise ValueError(f"{target.identifier}: missing edge(s): {missing}")

    missing_drug_edges = sorted(drug_node_ids - direct_drug_edges)
    if missing_drug_edges:
        missing = ", ".join(missing_drug_edges)
        raise ValueError(f"{target.identifier}: missing drug edge(s): {missing}")


def _canonical_drug_edge(
    record: dict[str, Any],
    drug_node: dict[str, Any],
    relation_evidence: list[dict[str, Any]],
) -> dict[str, Any]:
    drug_label = str(drug_node["label"])
    return _edge(
        "determinant",
        "confers resistance to (drug class)",
        "ARO:2000001",
        str(drug_node["node_id"]),
        f"CARD asserts that this ADC determinant confers resistance to {drug_label}.",
        *relation_evidence,
        _record_evidence(record),
        ADC_EVIDENCE,
        CLASS_C_EVIDENCE,
        BETA_LACTAMASE_EVIDENCE,
    )


def _graph(record: dict[str, Any], old_graph: dict[str, Any]) -> dict[str, Any]:
    record_evidence = _record_evidence(record)
    common_evidence = (
        record_evidence,
        ADC_EVIDENCE,
        CLASS_C_EVIDENCE,
        INACTIVATION_ENZYME_EVIDENCE,
        ANTIBIOTIC_INACTIVATION_EVIDENCE,
        BETA_LACTAMASE_EVIDENCE,
        AMPC_REACTION_EVIDENCE,
    )
    specific_evidence = (
        record_evidence,
        ADC_EVIDENCE,
        CLASS_C_EVIDENCE,
        BETA_LACTAMASE_EVIDENCE,
        SERINE_BETA_LACTAMASE_EVIDENCE,
        AMPC_REACTION_EVIDENCE,
    )
    catalytic_evidence = (
        record_evidence,
        ADC_EVIDENCE,
        CLASS_C_EVIDENCE,
        PROSITE_EVIDENCE,
        AMPC_REACTION_EVIDENCE,
    )
    drug_nodes = _drug_nodes(old_graph)
    drug_node_ids = {str(node["node_id"]) for node in drug_nodes}
    relation_evidence = _drug_relation_evidence(old_graph, drug_node_ids)

    direct_drug_edges = [
        _canonical_drug_edge(
            record,
            drug_node,
            relation_evidence[str(drug_node["node_id"])],
        )
        for drug_node in drug_nodes
    ]

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → class C serine beta-lactam hydrolysis",
        "description": (
            "Curated resistance-causation graph for ADC class C beta-lactamase "
            "hydrolysis of beta-lactam antibiotics."
        ),
        "nodes": [
            _determinant_node(record),
            copy.deepcopy(MECH0_NODE),
            copy.deepcopy(MECH1_NODE),
            *drug_nodes,
            copy.deepcopy(ACTIVE_SITE_NODE),
            copy.deepcopy(FOLD_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "CARD classifies ADC class C beta-lactamases under broad "
                "antibiotic inactivation.",
                *common_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Beta-lactamase antibiotic inactivation opens the beta-lactam "
                "ring and thereby causes resistance.",
                *common_evidence,
            ),
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech1",
                "CARD classifies ADC class C beta-lactamases under serine "
                "beta-lactam hydrolysis.",
                *specific_evidence,
            ),
            _edge(
                "mech1",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Serine beta-lactamase hydrolysis opens the beta-lactam ring "
                "and renders the antibiotic inactive.",
                *specific_evidence,
                ANTIBIOTIC_INACTIVATION_EVIDENCE,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "ADC beta-lactamases confer resistance through class C serine "
                "beta-lactam hydrolysis and antibiotic inactivation.",
                *common_evidence,
                SERINE_BETA_LACTAMASE_EVIDENCE,
            ),
            *direct_drug_edges,
            _edge(
                "active_site",
                "part of",
                "BFO:0000050",
                "determinant",
                "The class C Ser64 S-x-x-K active-site signature is part of "
                "the ADC beta-lactamase determinant.",
                *catalytic_evidence,
            ),
            _edge(
                "determinant",
                "member of",
                "RO:0002350",
                "fold",
                "The ADC determinant adopts the DD-peptidase/beta-lactamase "
                "fold associated with serine beta-lactamases.",
                record_evidence,
                ADC_EVIDENCE,
                CLASS_C_EVIDENCE,
                CATH_EVIDENCE,
                AMPC_REACTION_EVIDENCE,
            ),
            _edge(
                "active_site",
                "enables (serine beta-lactam hydrolysis)",
                "RO:0002327",
                "mech1",
                "The class C active site provides the catalytic serine used "
                "for beta-lactam hydrolysis.",
                *catalytic_evidence,
                SERINE_BETA_LACTAMASE_EVIDENCE,
            ),
        ],
    }


def _validate_record(record: dict[str, Any], target: Target) -> None:
    if record.get("identifier") != target.identifier:
        raise ValueError(
            f"{target.filename}: expected {target.identifier}, "
            f"found {record.get('identifier')}"
        )
    if not record.get("label"):
        raise ValueError(f"{target.identifier}: missing label")
    if not record.get("definition"):
        raise ValueError(f"{target.identifier}: missing definition")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError(f"{target.identifier}: expected exactly one resistance graph")
    _validate_graph(graphs[0], target)


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    _validate_record(record, target)

    out = copy.deepcopy(record)
    out["causal_graphs"] = [_graph(record, record["causal_graphs"][0])]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not an ADC target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_CURATOR not in out:
        out = append_to_section(out, "curation_history", _dump({"curation_history": [HISTORY_EVENT]}))
        changed = True

    if "&id" in out or "*id" in out:
        raise ValueError(f"{path}: YAML anchors leaked into output")
    return out, changed


def iter_target_paths(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if not path.is_dir():
        raise ValueError(f"{path} is neither a file nor a directory")
    return [path / target.filename for target in TARGETS]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR,
        help="ARO directory or one of the 329 ADC YAML files",
    )
    args = parser.parse_args(argv)

    changed = unchanged = 0
    problems: list[str] = []
    for path in iter_target_paths(args.path):
        if not path.exists():
            problems.append(f"{path}: missing")
            continue
        try:
            before = path.read_text(encoding="utf-8")
            after, did_change = enrich_text(before, path)
        except (OSError, ValueError, yaml.YAMLError) as exc:
            problems.append(str(exc))
            continue

        if not did_change:
            unchanged += 1
            continue

        changed += 1
        print(f"  {'wrote' if args.apply else 'would write'} {path.name}")
        if args.apply:
            path.write_text(after, encoding="utf-8")

    print(f"{'changed' if args.apply else 'would change'}: {changed}")
    print(f"already enriched: {unchanged}")
    for problem in problems:
        print(f"PROBLEM: {problem}", file=sys.stderr)
    if not args.apply:
        print("dry run -- pass --apply to write")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
