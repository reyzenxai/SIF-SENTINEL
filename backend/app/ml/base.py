"""
Base SIF classifier interface (SIH26165 — Phase 4).

Every baseline model (logistic regression, XGBoost, and — later —
transformer/embedding-based models) implements this interface. Nothing
outside app/ml/ should import a specific model class directly; go through
app/ml/registry.py so the "replaceable model" requirement in the brief
actually holds in practice, not just in theory.

Design choice worth documenting: models here are trained as BINARY
SIF-vs-NON_SIF classifiers (dropping weakly-labelled UNCERTAIN rows from
training), and UNCERTAIN is then produced at *inference* time by
thresholding the predicted P(SIF) into three zones. This is deliberate: a
3-way classifier trained on a heuristic-derived UNCERTAIN class would just
be learning to reproduce arbitrary threshold boundaries, which is circular.
Producing UNCERTAIN via a probability band is the same mechanism real
uncertainty-aware safety classifiers use, and it's the mechanism that will
keep working once training swaps to real human labels.
"""
import datetime as dt
from abc import ABC, abstractmethod
from typing import Optional

import joblib
import numpy as np

from app.core.canonical_schema import SIFLabel

# Probability thresholds mapping P(SIF) -> {NON_SIF, UNCERTAIN, SIF}.
# Intentionally NOT 0.5/0.5 — see module docstring in labeling.py for why a
# wide uncertain band is the safety-appropriate default for this system.
SIF_THRESHOLD_HIGH = 0.65
SIF_THRESHOLD_LOW = 0.35


def label_and_confidence_from_probability(p_sif: float) -> tuple[str, str]:
    """Map a raw P(SIF) into (sif_label, confidence band)."""
    if p_sif >= SIF_THRESHOLD_HIGH:
        label = SIFLabel.SIF.value
    elif p_sif <= SIF_THRESHOLD_LOW:
        label = SIFLabel.NON_SIF.value
    else:
        label = SIFLabel.UNCERTAIN.value

    distance_from_center = abs(p_sif - 0.5)
    if distance_from_center >= 0.35:
        confidence = "HIGH"
    elif distance_from_center >= 0.15:
        confidence = "MEDIUM"
    else:
        confidence = "LOW"
    return label, confidence


class BaseSIFClassifier(ABC):
    model_type: str = "base"

    def __init__(self):
        self.pipeline = None          # sklearn Pipeline, set by fit()/load()
        self.trained_at: Optional[str] = None
        self.n_train: int = 0

    @abstractmethod
    def _build_pipeline(self):
        """Return an unfit sklearn Pipeline (featurizer + classifier)."""
        ...

    def fit(self, texts: list[str], binary_labels: list[int]):
        """binary_labels: 1 = SIF, 0 = NON_SIF. UNCERTAIN rows must already
        be excluded by the caller (see train.py)."""
        self.pipeline = self._build_pipeline()
        self.pipeline.fit(texts, binary_labels)
        self.trained_at = dt.datetime.utcnow().isoformat()
        self.n_train = len(texts)
        return self

    def predict_proba_sif(self, texts: list[str]) -> np.ndarray:
        if self.pipeline is None:
            raise RuntimeError(f"{self.model_type} classifier has not been trained/loaded")
        proba = self.pipeline.predict_proba(texts)
        # locate the column for the positive (SIF=1) class defensively —
        # sklearn orders columns by sorted class label, which is [0, 1] here,
        # but this avoids silently transposing predictions if that ever changes.
        classes = list(self.pipeline.named_steps["clf"].classes_)
        sif_col = classes.index(1)
        return proba[:, sif_col]

    def save(self, path: str):
        joblib.dump(
            {"pipeline": self.pipeline, "model_type": self.model_type,
             "trained_at": self.trained_at, "n_train": self.n_train},
            path,
        )

    @classmethod
    def load(cls, path: str) -> "BaseSIFClassifier":
        payload = joblib.load(path)
        instance = cls()
        instance.pipeline = payload["pipeline"]
        instance.trained_at = payload.get("trained_at")
        instance.n_train = payload.get("n_train", 0)
        return instance
