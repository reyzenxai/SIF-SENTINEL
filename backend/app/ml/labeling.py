"""
Weak-label bootstrap (SIH26165 — Phase 4 scaffolding).

============================================================================
IMPORTANT — READ BEFORE USING
============================================================================
There is currently no hand-labelled or OIL-provided SIF ground truth
anywhere in this project. To make the classifier architecture testable and
benchmarkable today, this module derives a *heuristic* SIF/NON_SIF/UNCERTAIN
label from the existing deterministic risk engine (severity + control-failure
+ consequence scoring) and ontology extraction.

This is weak supervision, not ground truth. A model trained only on these
labels is learning to approximate the existing rule-based risk engine, not
to detect real SIF potential in raw text — which is precisely the trap the
brief warns against ("Do NOT simply train injury=yes -> SIF"). It exists so:

  1. The ML training/evaluation harness (features, models, metrics, model
     registry) can be built, run, and unit-tested NOW, without OIL data.
  2. Once real annotations exist (Phase 13's human-review workflow, or an
     OIL export that already carries expert-reviewed labels), the exact
     same training pipeline swaps this bootstrap out for real labels with
     a one-line change (see train.py --label-source).

Every model trained from these labels is tagged "label_source":
"weak_bootstrap_v1" in its manifest entry (see registry.py) specifically so
nobody can accidentally present it, or its accuracy numbers, as if it were
trained on real annotated SIF outcomes.
============================================================================
"""
from app.core.canonical_schema import SIFLabel

# Heuristic thresholds against the EXISTING risk engine's 0-100 overall_sif_score
# (app/services/risk_engine.py). Intentionally conservative: a wide UNCERTAIN
# band in the middle, because forcing a binary call here would defeat the
# entire point of having an UNCERTAIN label in the first place.
_SIF_FLOOR = 65.0       # at/above this heuristic score -> weak-labelled SIF
_NON_SIF_CEILING = 30.0  # at/below this -> weak-labelled NON_SIF
# Anything in between -> UNCERTAIN (by far the most defensible bucket for a
# heuristic label, and it also gives the annotation workflow / active
# learning loop, Phase 13, a natural place to prioritize human review).


def weak_label_from_risk_score(overall_sif_score: float) -> SIFLabel:
    if overall_sif_score is None:
        return SIFLabel.UNCERTAIN
    if overall_sif_score >= _SIF_FLOOR:
        return SIFLabel.SIF
    if overall_sif_score <= _NON_SIF_CEILING:
        return SIFLabel.NON_SIF
    return SIFLabel.UNCERTAIN


LABEL_SOURCE_TAG = "weak_bootstrap_v1"
