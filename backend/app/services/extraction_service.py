"""
NLP Extraction Service.

Hybrid design per spec section 11: attempt LLM-based structured extraction
if an API key is configured; otherwise (or on failure) fall back to
deterministic rule-based/ontology keyword matching. This fallback is not a
degraded stub — it is the documented, always-available extraction path.
"""
import re
import json
from app.core.config import LLM_ENABLED, ANTHROPIC_API_KEY
from app.services.ontology import FLAT_ONTOLOGY, ACTIVITY_KEYWORDS

EQUIPMENT_WORDS = ["pump", "panel", "valve", "compressor", "crane", "ladder", "vehicle",
                   "forklift", "scaffold", "generator", "pipeline", "tank", "hoist", "conveyor"]


def _find_evidence_sentence(text: str, keyword: str) -> str:
    sentences = re.split(r'(?<=[.!?])\s+', text)
    for s in sentences:
        if keyword.lower() in s.lower():
            return s.strip()
    return text.strip()


def rule_based_extract(description: str) -> dict:
    text_lower = description.lower()
    best_match = None
    evidence = []

    for entry in FLAT_ONTOLOGY:
        hits = [kw for kw in entry["keywords"] if kw in text_lower]
        if hits:
            score = len(hits)
            if best_match is None or score > best_match["_score"]:
                best_match = {**entry, "_score": score, "_hits": hits}

    activity = None
    for act, kws in ACTIVITY_KEYWORDS.items():
        if any(kw in text_lower for kw in kws):
            activity = act
            break

    equipment = None
    for eq in EQUIPMENT_WORDS:
        if eq in text_lower:
            equipment = eq
            break

    if best_match:
        for hit in best_match["_hits"]:
            evidence.append(_find_evidence_sentence(description, hit))
        hazard = best_match["subcategory"]
        hazard_category = best_match["hazard_category"]
        control_failure = best_match["subcategory"] if "failure" in best_match["subcategory"].lower() or \
            "loto" in best_match["subcategory"].lower() or "isolation" in best_match["subcategory"].lower() or \
            "permit" in best_match["subcategory"].lower() else None
        potential_consequence = best_match["potential_consequence"]
        # confidence scales with number of keyword hits, capped
        confidence = min(0.55 + 0.15 * best_match["_score"], 0.92)
        sif_relevance = min(0.5 + 0.14 * best_match["_score"], 0.95)
    else:
        hazard = None
        hazard_category = None
        control_failure = None
        potential_consequence = None
        confidence = 0.3
        sif_relevance = 0.15
        evidence = [description[:160]]

    unsafe_act = None
    unsafe_condition = None
    if any(w in text_lower for w in ["entered", "proceeded", "bypassed", "did not verify", "failed to", "without checking"]):
        unsafe_act = _find_evidence_sentence(description, "entered") if "entered" in text_lower else description.split(".")[0].strip()
    else:
        unsafe_condition = description.split(".")[0].strip()

    return {
        "activity": activity,
        "hazard": hazard,
        "hazard_category": hazard_category,
        "unsafe_act": unsafe_act,
        "unsafe_condition": unsafe_condition,
        "control_failure": control_failure,
        "equipment": equipment,
        "potential_consequence": potential_consequence,
        "exposure_context": activity or "general operations",
        "sif_relevance_score": round(sif_relevance, 2),
        "extraction_confidence": round(confidence, 2),
        "extraction_method": "rule_based",
        "evidence_spans": list(dict.fromkeys(evidence))[:3],
    }


def llm_extract(description: str) -> dict | None:
    """Attempt LLM-based extraction via the Anthropic API. Returns None on any
    failure so the caller can gracefully fall back to rule_based_extract."""
    if not LLM_ENABLED:
        return None
    try:
        import urllib.request

        prompt = f"""Extract structured safety information from this industrial safety report as JSON only, no prose.
Report: "{description}"

Return exactly this JSON shape:
{{"activity": "...", "hazard": "...", "hazard_category": "one of Electrical/Working at Height/Vehicle / Mobile Equipment/Confined Space/Process Safety/Permit to Work/PPE/Other", "unsafe_act": "... or null", "unsafe_condition": "... or null", "control_failure": "... or null", "equipment": "... or null", "potential_consequence": "...", "sif_relevance_score": 0.0}}"""

        body = json.dumps({
            "model": "claude-sonnet-4-6",
            "max_tokens": 400,
            "messages": [{"role": "user", "content": prompt}],
        }).encode()

        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=body,
            headers={
                "Content-Type": "application/json",
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
            },
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        text = "".join(b.get("text", "") for b in data.get("content", []))
        text = text.strip().strip("`").replace("json\n", "")
        parsed = json.loads(text)
        parsed["extraction_confidence"] = 0.88
        parsed["extraction_method"] = "llm"
        parsed["exposure_context"] = parsed.get("activity") or "general operations"
        parsed["evidence_spans"] = [description[:200]]
        return parsed
    except Exception:
        return None


def extract(description: str) -> dict:
    """Public entry point: try LLM, fall back to rule-based. Always returns
    a complete, usable extraction dict."""
    result = llm_extract(description)
    if result is None:
        result = rule_based_extract(description)
        result["ai_enrichment_note"] = "AI enrichment unavailable; rule-based analysis used." if LLM_ENABLED else None
    return result
