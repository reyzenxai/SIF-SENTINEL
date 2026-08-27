"""
Evaluation harness (SIH26165 — Phase 4).

Per the brief: accuracy is explicitly the wrong headline metric here (a
model predicting NON_SIF for everything can look "accurate" on an
imbalanced dataset while being useless). This module always reports
precision/recall/F1 per class, PR-AUC, SIF-class recall specifically, a
confusion matrix, and top-K recall (the fraction of true SIF reports
captured in the top-K% most-suspicious reports by predicted probability —
the number that actually matters for an HSE analyst triaging a queue).
"""
from typing import Optional

import numpy as np
from sklearn.metrics import (
    precision_recall_fscore_support,
    confusion_matrix,
    average_precision_score,
)

from app.core.canonical_schema import SIFLabel
from app.ml.schema import EvalMetrics

_CLASS_ORDER = [SIFLabel.NON_SIF.value, SIFLabel.UNCERTAIN.value, SIFLabel.SIF.value]


def top_k_recall(y_true_binary: np.ndarray, y_score: np.ndarray, k_fraction: float = 0.2) -> Optional[float]:
    """Of all TRUE SIF cases, what fraction fall in the top k_fraction of
    reports ranked by predicted P(SIF)? This is the practical triage metric:
    if an HSE team can only review the top 20% of a queue, how much of the
    real SIF signal do they actually see?"""
    n_positive = int(y_true_binary.sum())
    if n_positive == 0 or len(y_score) == 0:
        return None
    k = max(1, int(round(len(y_score) * k_fraction)))
    top_k_idx = np.argsort(-y_score)[:k]
    captured = int(y_true_binary[top_k_idx].sum())
    return round(captured / n_positive, 4)


def evaluate(
    y_true_3way: list[str],
    y_pred_3way: list[str],
    y_true_binary_for_proba: Optional[np.ndarray] = None,
    y_score_for_proba: Optional[np.ndarray] = None,
    n_train: int = 0,
) -> EvalMetrics:
    """
    y_true_3way / y_pred_3way: full held-out set, values in {NON_SIF, UNCERTAIN, SIF}.
    y_true_binary_for_proba / y_score_for_proba: the SUBSET of the held-out set
        that had a non-UNCERTAIN weak label (see labeling.py) — PR-AUC and
        top-K recall are only meaningful against a binary ground truth.
    """
    precision, recall, f1, support = precision_recall_fscore_support(
        y_true_3way, y_pred_3way, labels=_CLASS_ORDER, zero_division=0
    )
    cm = confusion_matrix(y_true_3way, y_pred_3way, labels=_CLASS_ORDER).tolist()

    sif_idx = _CLASS_ORDER.index(SIFLabel.SIF.value)
    sif_recall = float(recall[sif_idx])

    pr_auc = None
    tk_recall = None
    if y_true_binary_for_proba is not None and y_score_for_proba is not None and len(y_score_for_proba) > 0:
        if y_true_binary_for_proba.sum() > 0:
            pr_auc = round(float(average_precision_score(y_true_binary_for_proba, y_score_for_proba)), 4)
        tk_recall = top_k_recall(y_true_binary_for_proba, y_score_for_proba)

    return EvalMetrics(
        precision=round(float(np.mean(precision)), 4),
        recall=round(float(np.mean(recall)), 4),
        f1=round(float(np.mean(f1)), 4),
        pr_auc=pr_auc,
        sif_recall=round(sif_recall, 4),
        top_k_recall=tk_recall,
        confusion_matrix=cm,
        support={cls: int(s) for cls, s in zip(_CLASS_ORDER, support)},
        n_train=n_train,
        n_eval=len(y_true_3way),
    )
