"""
SIF prediction service (SIH26165 — Phase 4).

The ONLY module app/services/pipeline.py should import from app/ml/. Wraps
model loading + inference behind a call that can never crash report
ingestion: if no model has been trained yet, or the artifact fails to load
for any reason, predict() returns None and the caller leaves
SIFAssessment.sif_label / sif_confidence as their existing NULL defaults
(added in Phase 2) rather than raising.
"""
from typing import Optional

from app.ml import registry
from app.ml.base import label_and_confidence_from_probability
from app.ml.schema import SIFPrediction

_cached_classifier = None
_cached_entry = None
_cache_checked_version = None


def _get_classifier():
    global _cached_classifier, _cached_entry, _cache_checked_version
    active = registry.get_active_entry()
    active_version = active["model_version"] if active else None

    if active_version != _cache_checked_version:
        # active model changed (freshly trained/activated) since last check — reload
        _cached_classifier, _cached_entry = registry.load_active_classifier()
        _cache_checked_version = active_version

    return _cached_classifier, _cached_entry


def predict(report_text: str) -> Optional[SIFPrediction]:
    if not report_text or not report_text.strip():
        return None

    classifier, entry = _get_classifier()
    if classifier is None:
        return None

    try:
        p_sif = float(classifier.predict_proba_sif([report_text])[0])
    except Exception:
        return None

    label, confidence = label_and_confidence_from_probability(p_sif)
    return SIFPrediction(
        sif_label=label,
        sif_probability=round(p_sif, 4),
        confidence=confidence,
        model_version=entry["model_version"],
        label_source=entry.get("label_source", "unknown"),
    )
