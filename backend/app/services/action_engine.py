"""
Action Engine — generates prioritized, evidence-tied preventive recommendations.
Prototype recommendation — not official OIL policy.
"""

ACTION_TEMPLATES = {
    "Electrical": [
        "Conduct targeted LOTO (Lock-Out/Tag-Out) audit at affected locations",
        "Review electrical isolation verification procedure with maintenance crews",
        "Conduct contractor safety briefing on energized-equipment hazards",
    ],
    "Working at Height": [
        "Inspect fall-protection equipment availability and condition at affected sites",
        "Reinforce mandatory harness/anchor-point checks before elevated work",
        "Audit ladder and edge-protection controls at flagged locations",
    ],
    "Vehicle / Mobile Equipment": [
        "Review pedestrian-vehicle segregation controls at affected sites",
        "Audit reversing alarms and spotter procedures for mobile equipment",
        "Conduct driver safety refresher for contractors involved",
    ],
    "Confined Space": [
        "Audit confined-space entry permits and gas-testing compliance",
        "Verify rescue plan and standby-attendant procedures at affected sites",
    ],
    "Process Safety": [
        "Inspect containment integrity at flagged equipment/locations",
        "Review pressure-relief and leak-detection maintenance records",
    ],
    "Permit to Work": [
        "Audit permit-to-work issuance and verification process",
        "Conduct refresher training on PTW compliance for affected departments",
    ],
    "PPE": [
        "Audit PPE availability and compliance at affected sites",
        "Reinforce PPE requirements in toolbox talks for affected contractors",
    ],
}

GENERIC_ACTIONS = [
    "Inspect affected locations for recurring control failures",
    "Review incident trend with site safety officers",
]


def generate_actions(pattern_summary: dict) -> list[dict]:
    """Returns list of {priority, action, rationale, evidence_count}."""
    hazard = pattern_summary.get("common_hazard", "")
    sif_score = pattern_summary.get("sif_score", 50)
    report_count = pattern_summary.get("report_count", 0)
    trend = pattern_summary.get("trend", "stable")

    if sif_score >= 80:
        priority = "CRITICAL"
    elif sif_score >= 60:
        priority = "HIGH"
    elif sif_score >= 35:
        priority = "MODERATE"
    else:
        priority = "LOW"

    templates = ACTION_TEMPLATES.get(hazard, []) + GENERIC_ACTIONS
    actions = []
    for i, action_text in enumerate(templates[:5]):
        rationale = (
            f"Prototype recommendation — based on {report_count} linked reports showing a "
            f"{trend} trend in {hazard.lower() if hazard else 'related'} precursors "
            f"(SIF score {sif_score}/100)."
        )
        actions.append({
            "priority": priority if i == 0 else ("HIGH" if priority == "CRITICAL" else priority),
            "action": action_text,
            "rationale": rationale,
            "evidence_count": report_count,
        })
    return actions
