"""
Extensible SIF Safety Ontology.
Prototype methodology — configurable for OIL's approved safety framework.

Each category carries keyword triggers (used by the rule-based extraction
fallback) and a nominal potential consequence, used purely for the prototype's
deterministic/explainable scoring path.
"""

SAFETY_ONTOLOGY = {
    "Electrical": {
        "subcategories": {
            "Energized Equipment": ["energized", "live equipment", "live panel", "live wire", "not de-energized", "remained live"],
            "LOTO Failure": ["loto", "lock-out", "lockout", "tagout", "tag-out", "loto checklist", "loto verification"],
            "Isolation Failure": ["isolation", "isolate", "isolated", "not isolated", "isolation verification", "electrical isolation"],
            "Arc-Flash Exposure": ["arc flash", "arc-flash", "flashover"],
        },
        "potential_consequence": "Electrical shock / electrocution / serious injury",
    },
    "Working at Height": {
        "subcategories": {
            "Missing Fall Protection": ["no harness", "without harness", "without a secured harness", "fall protection",
                                        "no fall arrest", "fall arrest lanyard", "unsecured harness", "without edge protection"],
            "Unsafe Ladder": ["unsafe ladder", "damaged ladder", "ladder not secured", "faulty ladder",
                              "was damaged and not tagged", "ladder used for elevated work was damaged"],
            "Edge Exposure": ["open edge", "unprotected edge", "edge exposure", "no guardrail", "missing barricade",
                              "anchor point", "scaffold inspection tag was expired"],
        },
        "potential_consequence": "Fall from height / serious injury or fatality",
    },
    "Vehicle / Mobile Equipment": {
        "subcategories": {
            "Pedestrian Interaction": ["pedestrian", "struck by vehicle", "vehicle-pedestrian", "near miss with vehicle"],
            "Reversing": ["reversing", "reverse gear", "backing up", "no reverse alarm", "reverse alarm",
                          "backed up without a spotter"],
            "Blind Spot": ["blind spot", "poor visibility", "obstructed view", "spotter not present",
                           "vehicle movement zone", "designated walkway"],
        },
        "potential_consequence": "Vehicle strike / crush injury",
    },
    "Confined Space": {
        "subcategories": {
            "Gas Exposure": ["gas exposure", "toxic gas", "h2s", "oxygen deficient", "gas test", "gas testing",
                              "oxygen levels", "confined space entry", "confined space"],
            "Permit Failure": ["confined space permit", "no entry permit", "entry permit for the vessel"],
            "Rescue Failure": ["no rescue plan", "rescue equipment unavailable", "rescue equipment was unavailable",
                                "standby attendant absent", "standby attendant was absent"],
        },
        "potential_consequence": "Asphyxiation / toxic exposure",
    },
    "Process Safety": {
        "subcategories": {
            "Loss of Containment": ["loss of containment", "release of hydrocarbon", "tank overflow"],
            "Pressure Release": ["pressure release", "over-pressure", "relief valve", "pressure surge"],
            "Leak": ["pipeline leak", "flange leak"],
        },
        "potential_consequence": "Fire / explosion / toxic release",
    },
    "Permit to Work": {
        "subcategories": {
            "Missing Permit": ["no permit", "work without permit", "permit not issued", "missing ptw",
                              "without a valid permit", "without an approved hot work permit", "hot work permit",
                              "without a signed permit-to-work"],
            "Permit Verification Failure": ["permit not verified", "permit verification failure", "expired permit",
                                            "permit not signed", "permit-to-work was not verified",
                                            "without permit verification", "permit conditions were not reviewed"],
        },
        "potential_consequence": "Uncontrolled hazardous work / serious injury",
    },
    "PPE": {
        "subcategories": {
            "Missing PPE": ["no ppe", "without ppe", "ppe not worn", "missing helmet", "no gloves", "no safety glasses"],
            "Incorrect PPE": ["incorrect ppe", "wrong ppe", "inadequate ppe", "damaged ppe"],
        },
        "potential_consequence": "Injury from unprotected exposure",
    },
}

ACTIVITY_KEYWORDS = {
    "maintenance": ["maintenance", "repair", "servicing", "overhaul"],
    "inspection": ["inspection", "inspecting", "walkdown", "audit"],
    "operations": ["operating", "operation", "startup", "shutdown"],
    "excavation": ["excavation", "digging", "trenching"],
    "hot work": ["hot work", "welding", "grinding", "cutting"],
    "lifting": ["lifting", "crane operation", "rigging"],
    "transport": ["driving", "transport", "vehicle movement"],
}

# INCIDENT added for SIH26165 Phase 2: OSHA/NIOSH adapters ingest actual
# fatality/severe-injury records, which aren't unsafe-act/condition/near-miss
# reports — they're the "already happened" ground truth the near-miss data
# is being used to predict toward.
REPORT_TYPES = ["UNSAFE_ACT", "UNSAFE_CONDITION", "NEAR_MISS", "INCIDENT"]


def flatten_ontology():
    """Return a flat list of {hazard_category, subcategory, keywords, potential_consequence}."""
    flat = []
    for category, data in SAFETY_ONTOLOGY.items():
        for sub, keywords in data["subcategories"].items():
            flat.append({
                "hazard_category": category,
                "subcategory": sub,
                "keywords": keywords,
                "potential_consequence": data["potential_consequence"],
            })
    return flat


FLAT_ONTOLOGY = flatten_ontology()
