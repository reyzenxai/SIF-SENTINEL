"""
Model registry (SIH26165 — Phase 4, and groundwork for Phase 15's data/model
versioning requirement).

Tracks every trained SIF classifier in a JSON manifest: model version,
model type, dataset version, training timestamp, feature description, label
definitions, evaluation metrics, and label source (see labeling.py — this is
what stops a weak-bootstrap-trained model from silently being treated as if
it were trained on real ground truth). Exactly one model may be "active" at
a time; that's the one app/ml/predict_service.py loads for inference.
"""
import datetime as dt
import json
import uuid
from pathlib import Path
from typing import Optional

from app.core.config import MODELS_DIR
from app.ml.model_logreg import LogRegSIFClassifier
from app.ml.model_xgboost import XGBoostSIFClassifier

_MANIFEST_PATH = Path(MODELS_DIR) / "manifest.json"

_MODEL_CLASSES = {
    "tfidf_logreg": LogRegSIFClassifier,
    "tfidf_xgboost": XGBoostSIFClassifier,
}


def _load_manifest() -> list[dict]:
    if not _MANIFEST_PATH.exists():
        return []
    with open(_MANIFEST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_manifest(entries: list[dict]):
    with open(_MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, default=str)


def register_model(
    classifier,
    dataset_version: str,
    metrics: dict,
    label_source: str,
    label_definitions: dict,
    features_description: str,
    activate: bool = True,
) -> dict:
    """Save a trained classifier's artifact + manifest entry. Returns the entry."""
    model_version = f"{classifier.model_type}-{dt.datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}"
    artifact_path = str(Path(MODELS_DIR) / f"{model_version}.joblib")
    classifier.save(artifact_path)

    entries = _load_manifest()
    if activate:
        for e in entries:
            e["active"] = False

    entry = {
        "model_version": model_version,
        "model_type": classifier.model_type,
        "dataset_version": dataset_version,
        "trained_at": classifier.trained_at,
        "n_train": classifier.n_train,
        "features": features_description,
        "label_definitions": label_definitions,
        "label_source": label_source,
        "metrics": metrics,
        "artifact_path": artifact_path,
        "active": activate,
    }
    entries.append(entry)
    _save_manifest(entries)
    return entry


def list_models() -> list[dict]:
    return _load_manifest()


def get_active_entry() -> Optional[dict]:
    for e in _load_manifest():
        if e.get("active"):
            return e
    return None


def set_active(model_version: str) -> dict:
    entries = _load_manifest()
    found = None
    for e in entries:
        if e["model_version"] == model_version:
            e["active"] = True
            found = e
        else:
            e["active"] = False
    if not found:
        raise ValueError(f"No such model_version: {model_version}")
    _save_manifest(entries)
    return found


def load_active_classifier():
    """Returns (classifier_instance, manifest_entry) or (None, None) if no
    model has been trained/activated yet. Never raises — callers (the
    inference pipeline) must be able to run with zero trained models."""
    entry = get_active_entry()
    if entry is None:
        return None, None
    model_cls = _MODEL_CLASSES.get(entry["model_type"])
    if model_cls is None:
        return None, None
    try:
        classifier = model_cls.load(entry["artifact_path"])
    except Exception:
        return None, None
    return classifier, entry
