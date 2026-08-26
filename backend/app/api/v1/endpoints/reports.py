import csv
import io
import datetime as dt
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from app.db.session import get_db
from app.models.database import (
    SafetyReport, SafetyExtraction, SIFAssessment, ReportPatternLink, PatternCluster, RecommendedAction
)
from app.models.schemas import ReportIn
from app.services import pipeline, extraction_service, risk_engine
from app.services.pattern_engine import build_vectors
from sklearn.metrics.pairwise import cosine_similarity
from app.core.security import get_current_user

router = APIRouter()


def _report_summary(report: SafetyReport):
    assessment = report.assessment
    return {
        "id": report.id,
        "title": report.description[:80],
        "description": report.description,
        "report_type": report.report_type,
        "location": report.location,
        "site": report.site,
        "department": report.department,
        "contractor": report.contractor,
        "report_date": report.report_date.isoformat() if report.report_date else None,
        "severity": report.severity,
        "sif_score": assessment.overall_sif_score if assessment else None,
        "risk_level": assessment.risk_level if assessment else None,
        "hazard_category": report.extraction.hazard_category if report.extraction else None,
    }


@router.get("")
def list_reports(
    db: Session = Depends(get_db),
    site: str | None = None,
    department: str | None = None,
    contractor: str | None = None,
    report_type: str | None = None,
    hazard_category: str | None = None,
    risk_level: str | None = None,
    keyword: str | None = None,
    semantic_query: str | None = None,
    date_start: str | None = None,
    date_end: str | None = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
):
    q = db.query(SafetyReport)
    if site:
        q = q.filter(SafetyReport.site == site)
    if department:
        q = q.filter(SafetyReport.department == department)
    if contractor:
        q = q.filter(SafetyReport.contractor == contractor)
    if report_type:
        q = q.filter(SafetyReport.report_type == report_type)
    if date_start:
        q = q.filter(SafetyReport.report_date >= dt.datetime.fromisoformat(date_start))
    if date_end:
        q = q.filter(SafetyReport.report_date <= dt.datetime.fromisoformat(date_end))
    if keyword:
        q = q.filter(SafetyReport.description.ilike(f"%{keyword}%"))
    if hazard_category:
        q = q.join(SafetyExtraction).filter(SafetyExtraction.hazard_category == hazard_category)
    if risk_level:
        q = q.join(SIFAssessment).filter(SIFAssessment.risk_level == risk_level)

    total = q.count()
    reports = q.order_by(SafetyReport.report_date.desc()).offset((page - 1) * size).limit(size).all()

    results = [_report_summary(r) for r in reports]

    if semantic_query:
        # simple semantic search: TF-IDF cosine similarity against current page + a broader pool
        pool = db.query(SafetyReport).limit(1000).all()
        texts = [semantic_query] + [r.description for r in pool]
        matrix, _ = build_vectors(texts)
        sims = cosine_similarity(matrix[0:1], matrix[1:]).flatten()
        ranked = sorted(zip(pool, sims), key=lambda x: -x[1])[:size]
        results = [_report_summary(r) for r, s in ranked if s > 0.05]
        total = len(results)

    return {"reports": results, "total": total, "page": page, "size": size}


@router.get("/{report_id}")
def get_report(report_id: str, db: Session = Depends(get_db)):
    report = db.query(SafetyReport).filter_by(id=report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    ext = report.extraction
    assessment = report.assessment
    pattern_links = report.pattern_links
    patterns = []
    for link in pattern_links:
        p = link.pattern
        patterns.append({"id": p.id, "title": p.title, "sif_score": p.sif_score, "trend": p.trend})

    recs = []
    for link in pattern_links:
        for a in link.pattern.actions:
            recs.append({
                "id": a.id, "priority": a.priority, "action": a.action,
                "rationale": a.rationale, "evidence_count": a.evidence_count,
                "pattern_id": link.pattern.id, "pattern_title": link.pattern.title,
            })

    return {
        "report": {
            "id": report.id,
            "description": report.description,
            "report_type": report.report_type,
            "location": report.location,
            "site": report.site,
            "department": report.department,
            "contractor": report.contractor,
            "reporter_role": report.reporter_role,
            "report_date": report.report_date.isoformat() if report.report_date else None,
            "severity": report.severity,
            "is_synthetic": report.is_synthetic,
        },
        "extraction": {
            "activity": ext.activity if ext else None,
            "hazard": ext.hazard if ext else None,
            "hazard_category": ext.hazard_category if ext else None,
            "unsafe_act": ext.unsafe_act if ext else None,
            "unsafe_condition": ext.unsafe_condition if ext else None,
            "control_failure": ext.control_failure if ext else None,
            "equipment": ext.equipment if ext else None,
            "potential_consequence": ext.potential_consequence if ext else None,
            "exposure_context": ext.exposure_context if ext else None,
            "sif_relevance_score": ext.sif_relevance_score if ext else None,
            "extraction_confidence": ext.extraction_confidence if ext else None,
            "extraction_method": ext.extraction_method if ext else None,
            "evidence_spans": ext.evidence_spans if ext else [],
        } if ext else None,
        "assessment": {
            "severity_score": assessment.severity_score,
            "exposure_score": assessment.exposure_score,
            "control_failure_score": assessment.control_failure_score,
            "recurrence_score": assessment.recurrence_score,
            "consequence_score": assessment.consequence_score,
            "overall_sif_score": assessment.overall_sif_score,
            "risk_level": assessment.risk_level,
            "reasoning": assessment.reasoning,
        } if assessment else None,
        "patterns": patterns,
        "recommendations": recs,
    }


@router.post("")
def create_report(body: ReportIn, db: Session = Depends(get_db)):
    if not body.description or not body.description.strip():
        raise HTTPException(status_code=400, detail="Report description cannot be empty")
    report_data = body.dict()
    report = pipeline.ingest_report(db, report_data, is_synthetic=False)
    db.commit()

    # similar count against existing corpus via quick TF-IDF pass
    pool = db.query(SafetyReport).filter(SafetyReport.id != report.id).limit(1000).all()
    similar_count = 0
    if pool:
        texts = [report.description] + [r.description for r in pool]
        matrix, _ = build_vectors(texts)
        sims = cosine_similarity(matrix[0:1], matrix[1:]).flatten()
        similar_count = int((sims > 0.35).sum())

    extraction, assessment = pipeline.extract_and_assess_report(db, report, similar_count=similar_count)
    db.commit()

    return {
        "id": report.id,
        "title": report.description[:80],
        "status": "processed",
        "created_at": report.created_at.isoformat(),
        "sif_score": assessment.overall_sif_score,
        "risk_level": assessment.risk_level,
    }


def _background_pipeline_runner(reports_data: list[dict], is_synthetic: bool):
    from app.db.session import SessionLocal
    db = SessionLocal()
    try:
        pipeline.run_full_pipeline(db, reports_data, is_synthetic=is_synthetic)
    finally:
        db.close()


@router.post("/upload")
def upload_reports(
    file: UploadFile = File(...), 
    current_user: dict = Depends(get_current_user),
    background_tasks: BackgroundTasks = None
):
    try:
        content = file.file.read().decode("utf-8", errors="ignore")
        reader = csv.DictReader(io.StringIO(content))
        rows = list(reader)
        if not rows:
            raise HTTPException(status_code=400, detail="Empty or malformed CSV uploaded")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=400, detail="Malformed CSV uploaded")

    reports_data = []
    for row in rows:
        try:
            report_date = dt.datetime.fromisoformat(row.get("report_date")) if row.get("report_date") else dt.datetime.utcnow()
        except Exception:
            report_date = dt.datetime.utcnow()
        reports_data.append({
            "report_date": report_date,
            "report_type": row.get("report_type", "NEAR_MISS"),
            "location": row.get("location"),
            "site": row.get("site") or row.get("location"),
            "department": row.get("department"),
            "contractor": row.get("contractor"),
            "reporter_role": row.get("reporter_role"),
            "description": row.get("description", "").strip() or "No description provided",
            "severity": row.get("severity", "UNKNOWN"),
            "planted_pattern": row.get("planted_pattern") or None,
        })

    if background_tasks is not None:
        background_tasks.add_task(_background_pipeline_runner, reports_data, True)
    else:
        _background_pipeline_runner(reports_data, True)

    return {
        "message": "Reports uploaded. Processing in the background...",
        "reports_queued": len(reports_data),
    }


@router.delete("/reset")
def reset_all_data(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    db.query(RecommendedAction).delete()
    db.query(ReportPatternLink).delete()
    db.query(PatternCluster).delete()
    db.query(SIFAssessment).delete()
    db.query(SafetyExtraction).delete()
    db.query(SafetyReport).delete()
    db.commit()
    return {"message": "All report data cleared."}
