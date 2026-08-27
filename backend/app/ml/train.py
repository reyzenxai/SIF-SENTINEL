"""
Training entrypoint (SIH26165 — Phase 4).

Usage as a script:
    python -m app.ml.train --model tfidf_logreg
    python -m app.ml.train --model tfidf_xgboost --no-activate

Usage as a library (used by the /ml/train API endpoint):
    from app.ml.train import train_and_register
    entry = train_and_register(db, model_type="tfidf_logreg")

Label sources (see app/ml/labeling.py and the Annotation table, Phase 13):
  - "weak_bootstrap": always use the risk-engine-derived heuristic labels.
    Useful for exercising the ML pipeline before any human review exists.
  - "annotated": always use human-submitted annotations (Phase 13). Fails
    loudly if there isn't enough annotated data yet, rather than silently
    falling back — you don't want to think you trained on real labels when
    you didn't.
  - "auto" (default): use annotated data if there's enough of it
    (>= MIN_PER_CLASS_TO_TRAIN per class after dropping UNCERTAIN), otherwise
    fall back to the weak bootstrap. This is the active-learning loop the
    brief describes: bootstrap first, then graduate to real labels as the
    annotation queue (see app/api/v1/endpoints/annotations.py) gets worked.

Split strategy: temporal, not random — train on the older N%, evaluate on
the most recent (1-N)%, exactly as the brief specifies ("avoid random
leakage... prefer TRAIN -> older data, VALIDATION -> later data").
"""
import argparse
import datetime as dt

import numpy as np
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.canonical_schema import SIFLabel
from app.ml import registry, labeling
from app.ml.base import label_and_confidence_from_probability, SIF_THRESHOLD_HIGH, SIF_THRESHOLD_LOW
from app.ml.evaluate import evaluate
from app.ml.model_logreg import LogRegSIFClassifier
from app.ml.model_xgboost import XGBoostSIFClassifier
from app.models.database import SafetyReport, SIFAssessment, Annotation

_MODEL_CLASSES = {
    "tfidf_logreg": LogRegSIFClassifier,
    "tfidf_xgboost": XGBoostSIFClassifier,
}

MIN_REPORTS_TO_TRAIN = 30
MIN_PER_CLASS_TO_TRAIN = 5

ANNOTATED_LABEL_SOURCE_TAG = "human_annotated_v1"


def _load_weak_labelled_rows(db: Session) -> list[dict]:
    """Every assessed report, labelled via the risk-engine heuristic bootstrap."""
    rows = (
        db.query(SafetyReport.description, SIFAssessment.overall_sif_score, SafetyReport.report_date)
        .join(SIFAssessment, SIFAssessment.report_id == SafetyReport.id)
        .filter(SafetyReport.description.isnot(None))
        .order_by(SafetyReport.report_date.asc())
        .all()
    )
    out = []
    for description, overall_sif_score, report_date in rows:
        if not description or not description.strip():
            continue
        weak_label = labeling.weak_label_from_risk_score(overall_sif_score)
        out.append({"text": description, "label": weak_label, "date": report_date})
    return out


def _load_annotated_rows(db: Session) -> list[dict]:
    """Every report with at least one human annotation, using the MOST
    RECENT annotation per report (see Annotation model docstring)."""
    latest_ids_subq = (
        db.query(Annotation.report_id, func.max(Annotation.created_at).label("max_created"))
        .group_by(Annotation.report_id)
        .subquery()
    )
    rows = (
        db.query(Annotation.sif_label, SafetyReport.description, SafetyReport.report_date)
        .join(SafetyReport, SafetyReport.id == Annotation.report_id)
        .join(
            latest_ids_subq,
            (Annotation.report_id == latest_ids_subq.c.report_id)
            & (Annotation.created_at == latest_ids_subq.c.max_created),
        )
        .order_by(SafetyReport.report_date.asc())
        .all()
    )
    out = []
    for sif_label, description, report_date in rows:
        if not description or not description.strip():
            continue
        try:
            label = SIFLabel(sif_label)
        except ValueError:
            continue
        out.append({"text": description, "label": label, "date": report_date})
    return out


def _binary_class_counts(rows: list[dict]) -> dict:
    return {
        SIFLabel.SIF.value: sum(1 for r in rows if r["label"] == SIFLabel.SIF),
        SIFLabel.NON_SIF.value: sum(1 for r in rows if r["label"] == SIFLabel.NON_SIF),
    }


def _resolve_rows(db: Session, label_source: str) -> tuple[list[dict], str]:
    """Returns (rows, resolved_label_source_tag)."""
    if label_source == "weak_bootstrap":
        return _load_weak_labelled_rows(db), labeling.LABEL_SOURCE_TAG

    annotated_rows = _load_annotated_rows(db)
    annotated_counts = _binary_class_counts(annotated_rows)
    annotated_sufficient = min(annotated_counts.values(), default=0) >= MIN_PER_CLASS_TO_TRAIN

    if label_source == "annotated":
        if not annotated_sufficient:
            raise ValueError(
                f"Not enough human-annotated data yet to train exclusively on it: "
                f"{annotated_counts} (need >= {MIN_PER_CLASS_TO_TRAIN} per class). "
                f"Review more reports via /annotations/queue, or use label_source="
                f"'auto' to fall back to the weak bootstrap for now."
            )
        return annotated_rows, ANNOTATED_LABEL_SOURCE_TAG

    if label_source == "auto":
        if annotated_sufficient:
            return annotated_rows, ANNOTATED_LABEL_SOURCE_TAG
        return _load_weak_labelled_rows(db), labeling.LABEL_SOURCE_TAG

    raise ValueError(f"Unknown label_source '{label_source}'. Use weak_bootstrap, annotated, or auto.")


def train_and_register(
    db: Session,
    model_type: str = "tfidf_logreg",
    activate: bool = True,
    eval_fraction: float = 0.2,
    label_source: str = "auto",
) -> dict:
    if model_type not in _MODEL_CLASSES:
        raise ValueError(f"Unknown model_type '{model_type}'. Available: {list(_MODEL_CLASSES)}")

    rows, resolved_label_source = _resolve_rows(db, label_source)
    if resolved_label_source == labeling.LABEL_SOURCE_TAG and len(rows) < MIN_REPORTS_TO_TRAIN:
        # This floor only makes sense for the weak bootstrap, where a large
        # fraction of rows are expected to land in UNCERTAIN and get dropped
        # before training. Annotated data is validated by the per-class
        # check below instead — demanding 30 total human-reviewed reports
        # before ANY training run is possible would make the annotation
        # workflow needlessly slow to bootstrap from.
        raise ValueError(
            f"Only {len(rows)} labelled reports available (label_source="
            f"'{label_source}') — need at least {MIN_REPORTS_TO_TRAIN} to train "
            f"a baseline classifier. Seed/upload more reports, or annotate more "
            f"via /annotations/queue, first."
        )

    split_idx = int(len(rows) * (1 - eval_fraction))
    train_rows = rows[:split_idx]
    eval_rows = rows[split_idx:]

    # Binary training set: drop UNCERTAIN-labelled rows regardless of source
    # (see base.py docstring — UNCERTAIN is produced by thresholding at
    # inference time, not trained as a third class).
    train_binary = [r for r in train_rows if r["label"] != SIFLabel.UNCERTAIN]
    class_counts = _binary_class_counts(train_binary)
    if min(class_counts.values(), default=0) < MIN_PER_CLASS_TO_TRAIN:
        raise ValueError(
            f"Not enough examples per class in the training split: {class_counts}. "
            f"Need at least {MIN_PER_CLASS_TO_TRAIN} of each SIF/NON_SIF."
        )

    texts = [r["text"] for r in train_binary]
    binary_labels = [1 if r["label"] == SIFLabel.SIF else 0 for r in train_binary]

    classifier = _MODEL_CLASSES[model_type]()
    classifier.fit(texts, binary_labels)

    # --- Evaluation on the held-out (temporally later) split ---
    eval_texts = [r["text"] for r in eval_rows]
    p_sif = classifier.predict_proba_sif(eval_texts) if eval_texts else np.array([])
    y_pred_3way = [label_and_confidence_from_probability(p)[0] for p in p_sif]
    y_true_3way = [r["label"].value for r in eval_rows]

    binary_mask = np.array([r["label"] != SIFLabel.UNCERTAIN for r in eval_rows])
    y_true_binary = np.array([1 if r["label"] == SIFLabel.SIF else 0 for r in eval_rows])[binary_mask] \
        if len(eval_rows) else np.array([])
    y_score_binary = p_sif[binary_mask] if len(p_sif) else np.array([])

    metrics = evaluate(
        y_true_3way=y_true_3way,
        y_pred_3way=y_pred_3way,
        y_true_binary_for_proba=y_true_binary if len(y_true_binary) else None,
        y_score_for_proba=y_score_binary if len(y_score_binary) else None,
        n_train=len(train_binary),
    )

    dataset_version = (
        f"{resolved_label_source}_{dt.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}"
        f"_n{len(rows)}_train{len(train_binary)}_eval{len(eval_rows)}"
    )

    label_definitions = {
        "SIF": f"P(SIF) >= {SIF_THRESHOLD_HIGH}",
        "NON_SIF": f"P(SIF) <= {SIF_THRESHOLD_LOW}",
        "UNCERTAIN": f"{SIF_THRESHOLD_LOW} < P(SIF) < {SIF_THRESHOLD_HIGH}",
    }
    if resolved_label_source == labeling.LABEL_SOURCE_TAG:
        label_definitions["_training_label_definition"] = (
            "Training labels are heuristically bootstrapped from the existing "
            "rule-based risk engine's overall_sif_score (>=65 SIF, <=30 NON_SIF, "
            "else UNCERTAIN) — NOT hand-annotated or OIL-provided ground truth. "
            "See app/ml/labeling.py."
        )
    else:
        label_definitions["_training_label_definition"] = (
            "Training labels are human HSE-reviewer annotations submitted via "
            "/annotations — see app/models/database.py::Annotation and "
            "/annotations/export."
        )

    entry = registry.register_model(
        classifier,
        dataset_version=dataset_version,
        metrics=metrics.__dict__,
        label_source=resolved_label_source,
        label_definitions=label_definitions,
        features_description="TF-IDF, word 1-2 grams, max_features=20000, min_df=2, sublinear_tf",
        activate=activate,
    )
    return entry


def main():
    from app.db.session import SessionLocal

    parser = argparse.ArgumentParser(description="Train a baseline SIF classifier")
    parser.add_argument("--model", default="tfidf_logreg", choices=list(_MODEL_CLASSES))
    parser.add_argument("--label-source", default="auto", choices=["auto", "annotated", "weak_bootstrap"])
    parser.add_argument("--no-activate", action="store_true")
    parser.add_argument("--eval-fraction", type=float, default=0.2)
    args = parser.parse_args()

    db = SessionLocal()
    try:
        entry = train_and_register(
            db, model_type=args.model, activate=not args.no_activate,
            eval_fraction=args.eval_fraction, label_source=args.label_source,
        )
        print(f"Trained {entry['model_version']} (active={entry['active']}, label_source={entry['label_source']})")
        print("Metrics:", entry["metrics"])
    finally:
        db.close()


if __name__ == "__main__":
    main()
