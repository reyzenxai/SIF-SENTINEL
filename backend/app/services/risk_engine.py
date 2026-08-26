"""
SIF Risk Engine — transparent, component-visible scoring.
Prototype methodology — configurable for OIL's approved safety framework.
"""
from app.core.config import SIF_SCORE_WEIGHTS

SEVERITY_KEYWORDS_HIGH = ["electrocution", "fatality", "fall from height", "asphyxiation",
                          "explosion", "fire", "crush injury", "toxic"]


def compute_severity(extraction: dict) -> float:
    max_w = SIF_SCORE_WEIGHTS["severity"]
    consequence = (extraction.get("potential_consequence") or "").lower()
    if any(k in consequence for k in SEVERITY_KEYWORDS_HIGH):
        return max_w * 0.92
    if consequence:
        return max_w * 0.6
    return max_w * 0.25


def compute_control_failure(extraction: dict) -> float:
    max_w = SIF_SCORE_WEIGHTS["control_failure"]
    if extraction.get("control_failure"):
        return max_w * 0.9
    return max_w * 0.2


def compute_exposure(extraction: dict) -> float:
    max_w = SIF_SCORE_WEIGHTS["exposure"]
    activity = (extraction.get("activity") or "").lower()
    high_exposure_activities = ["maintenance", "hot work", "lifting", "excavation"]
    if activity in high_exposure_activities:
        return max_w * 0.85
    if activity:
        return max_w * 0.55
    return max_w * 0.3


def compute_recurrence(similar_report_count: int) -> float:
    max_w = SIF_SCORE_WEIGHTS["recurrence"]
    if similar_report_count <= 0:
        return max_w * 0.1
    # scales up to max around 20+ similar reports
    ratio = min(similar_report_count / 20.0, 1.0)
    return max_w * (0.2 + 0.8 * ratio)


def compute_consequence(extraction: dict) -> float:
    max_w = SIF_SCORE_WEIGHTS["consequence"]
    consequence = (extraction.get("potential_consequence") or "").lower()
    if any(k in consequence for k in SEVERITY_KEYWORDS_HIGH):
        return max_w * 0.95
    if consequence:
        return max_w * 0.5
    return max_w * 0.2


def risk_level_for_score(score: float) -> str:
    if score >= 80:
        return "CRITICAL"
    if score >= 60:
        return "HIGH"
    if score >= 35:
        return "MODERATE"
    return "LOW"


def assess(extraction: dict, similar_report_count: int = 0) -> dict:
    severity = round(compute_severity(extraction), 1)
    control_failure = round(compute_control_failure(extraction), 1)
    exposure = round(compute_exposure(extraction), 1)
    recurrence = round(compute_recurrence(similar_report_count), 1)
    consequence = round(compute_consequence(extraction), 1)

    total = round(severity + control_failure + exposure + recurrence + consequence, 1)
    total = min(total, 100.0)
    level = risk_level_for_score(total)

    reasoning = []
    if severity >= SIF_SCORE_WEIGHTS["severity"] * 0.8:
        reasoning.append("Potential severe consequence detected")
    if control_failure >= SIF_SCORE_WEIGHTS["control_failure"] * 0.8:
        reasoning.append("Critical safety-control failure detected")
    if similar_report_count >= 5:
        reasoning.append(f"Similar events repeated {similar_report_count} times")
    if exposure >= SIF_SCORE_WEIGHTS["exposure"] * 0.75:
        reasoning.append("High-risk activity detected")
    if extraction.get("hazard_category"):
        reasoning.append(f"Hazard category: {extraction['hazard_category']}")
    if not reasoning:
        reasoning.append("No significant SIF precursor indicators detected in current extraction")

    return {
        "severity_score": severity,
        "exposure_score": exposure,
        "control_failure_score": control_failure,
        "recurrence_score": recurrence,
        "consequence_score": consequence,
        "overall_sif_score": total,
        "risk_level": level,
        "reasoning": reasoning,
    }
