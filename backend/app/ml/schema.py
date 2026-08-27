"""Typed prediction result for the SIF classifier (SIH26165 — Phase 4)."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class SIFPrediction:
    sif_label: str            # "SIF" | "NON_SIF" | "UNCERTAIN"
    sif_probability: float    # model's raw P(SIF), 0-1
    confidence: str           # "HIGH" | "MEDIUM" | "LOW" — see models/base.py for banding
    model_version: str
    label_source: str         # e.g. "weak_bootstrap_v1" — see labeling.py. Surfaced all
                               # the way to the API response so the UI/analyst can see when
                               # a prediction came from a heuristic-trained model.


@dataclass
class EvalMetrics:
    precision: float
    recall: float
    f1: float
    pr_auc: Optional[float]
    sif_recall: float          # recall specifically on the SIF class — the number that
                                # actually matters for a safety-critical system
    top_k_recall: Optional[float]
    confusion_matrix: list      # 2D list, rows=true, cols=pred, over [NON_SIF, UNCERTAIN, SIF]
    support: dict                # per-class counts
    n_train: int
    n_eval: int
