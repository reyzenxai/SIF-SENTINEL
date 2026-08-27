"""
Human annotation + active learning workflow (SIH26165 — Phase 13).

This is what breaks the circularity flagged in Phase 4: a classifier
trained only on the rule-based risk engine's own output can't teach us
anything the risk engine didn't already know. Once enough human-reviewed
labels exist here, app/ml/train.py can train against real ground truth
instead of the weak_bootstrap_v1 heuristic — see label_source="annotated"/
"auto" there.

Active learning queue: rather than asking a human to label 100,000 OIL
reports in order, /annotations/queue prioritizes the reports the CURRENT
model is least sure about (predicted P(SIF) closest to 0.5) — the reports
where a human label actually teaches the model something. Before any model
exists, it falls back to prioritizing by how close the rule-based risk
score sits to its own midpoint, as a reasonable starting proxy.
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.database import SafetyReport, SIFAssessment, Annotation
from app.models.schemas import AnnotationIn
from app.ml import predict_service as sif_classifier
from app.ml.registry import get_active_entry

router = APIRouter()

# How many not-yet-annotated candidates to pull from the DB before ranking
# them for the queue. Keeps predict() calls bounded even on a large table.
_QUEUE_CANDIDATE_POOL = 300


@router.get("/queue")
def get_annotation_queue(
    limit: int = Query(default=20, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Reports most worth a human's time to review next, most-informative first."""
    annotated_report_ids = {a.report_id for a in db.query(Annotation.report_id).distinct()}

    candidates = (
        db.query(SafetyReport, SIFAssessment)
        .join(SIFAssessment, SIFAssessment.report_id == SafetyReport.id)
        .order_by(SafetyReport.created_at.desc())
        .limit(_QUEUE_CANDIDATE_POOL)
        .all()
    )
    candidates = [(r, a) for r, a in candidates if r.id not in annotated_report_ids]

    active_model = get_active_entry()
    scored = []
    for report, assessment in candidates:
        if active_model is not None:
            prediction = sif_classifier.predict(report.description)
            uncertainty = abs(prediction.sif_probability - 0.5) if prediction else 1.0
        else:
            # No model yet: proxy uncertainty using the rule-based risk score's
            # distance from its own midpoint (50) — reports the deterministic
            # engine itself is least confident about.
            score = assessment.overall_sif_score if assessment.overall_sif_score is not None else 100
            uncertainty = abs(score - 50) / 50
        scored.append((uncertainty, report, assessment))

    scored.sort(key=lambda x: x[0])  # most uncertain (lowest score) first
    top = scored[:limit]

    return {
        "queue": [
            {
                "report_id": r.id,
                "description": r.description,
                "report_type": r.report_type,
                "site": r.site,
                "risk_level": a.risk_level,
                "overall_sif_score": a.overall_sif_score,
                "current_sif_label_prediction": a.sif_label,
                "current_sif_confidence": a.sif_confidence,
                "uncertainty": round(u, 4),
            }
            for u, r, a in top
        ],
        "candidates_considered": len(candidates),
        "using_active_model": active_model is not None,
    }


@router.post("/{report_id}")
def submit_annotation(
    report_id: str,
    body: AnnotationIn,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    report = db.query(SafetyReport).filter(SafetyReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    if body.sif_label not in ("SIF", "NON_SIF", "UNCERTAIN"):
        raise HTTPException(status_code=400, detail="sif_label must be SIF, NON_SIF, or UNCERTAIN")

    annotation = Annotation(
        report_id=report_id,
        annotator=current_user.get("username", "unknown"),
        sif_label=body.sif_label,
        life_saving_rules=body.life_saving_rules,
        activity=body.activity,
        hazard=body.hazard,
        unsafe_act=body.unsafe_act,
        unsafe_condition=body.unsafe_condition,
        barrier_failure=body.barrier_failure,
        potential_consequence=body.potential_consequence,
        notes=body.notes,
    )
    db.add(annotation)
    db.commit()
    db.refresh(annotation)

    return {"message": "Annotation recorded.", "annotation_id": annotation.id}


@router.get("")
def list_annotations(
    limit: int = Query(default=50, le=500),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    total = db.query(Annotation).count()
    rows = (
        db.query(Annotation)
        .order_by(Annotation.created_at.desc())
        .offset(offset).limit(limit)
        .all()
    )
    return {
        "total": total,
        "annotations": [
            {
                "id": a.id, "report_id": a.report_id, "annotator": a.annotator,
                "sif_label": a.sif_label, "life_saving_rules": a.life_saving_rules,
                "created_at": a.created_at,
            }
            for a in rows
        ],
    }


@router.get("/export")
def export_annotations(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Training-ready export: one row per report's MOST RECENT annotation,
    joined with report text. This is the format app/ml/train.py's
    label_source='annotated' path consumes, and is also suitable for
    handing to an external labeling/QA tool."""
    latest_ids_subq = (
        db.query(Annotation.report_id, func.max(Annotation.created_at).label("max_created"))
        .group_by(Annotation.report_id)
        .subquery()
    )
    rows = (
        db.query(Annotation, SafetyReport.description)
        .join(SafetyReport, SafetyReport.id == Annotation.report_id)
        .join(
            latest_ids_subq,
            (Annotation.report_id == latest_ids_subq.c.report_id)
            & (Annotation.created_at == latest_ids_subq.c.max_created),
        )
        .all()
    )
    return {
        "count": len(rows),
        "records": [
            {
                "report_id": a.report_id,
                "report_text": text,
                "sif_label": a.sif_label,
                "life_saving_rules": a.life_saving_rules,
                "activity": a.activity,
                "hazard": a.hazard,
                "unsafe_act": a.unsafe_act,
                "unsafe_condition": a.unsafe_condition,
                "barrier_failure": a.barrier_failure,
                "potential_consequence": a.potential_consequence,
                "annotator": a.annotator,
                "annotated_at": a.created_at,
            }
            for a, text in rows
        ],
    }


@router.get("/stats")
def annotation_stats(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    total_reports = db.query(SafetyReport).count()
    annotated_reports = db.query(Annotation.report_id).distinct().count()
    by_label = dict(
        db.query(Annotation.sif_label, func.count(Annotation.id.distinct()))
        .group_by(Annotation.sif_label)
        .all()
    )
    return {
        "total_reports": total_reports,
        "annotated_reports": annotated_reports,
        "coverage_pct": round(100 * annotated_reports / total_reports, 2) if total_reports else 0,
        "label_distribution": by_label,
    }
