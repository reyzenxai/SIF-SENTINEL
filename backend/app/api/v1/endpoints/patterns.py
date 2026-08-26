from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.database import PatternCluster, ReportPatternLink

router = APIRouter()


def _pattern_summary(p: PatternCluster):
    return {
        "id": p.id,
        "title": p.title,
        "summary": p.description,
        "report_count": p.report_count,
        "locations": p.locations,
        "contractors": p.contractors,
        "departments": p.departments,
        "trend": p.trend,
        "trend_pct": p.trend_pct,
        "sif_score": p.sif_score,
        "sif_risk_level": (
            "CRITICAL" if p.sif_score >= 80 else
            "HIGH" if p.sif_score >= 60 else
            "MODERATE" if p.sif_score >= 35 else "LOW"
        ),
        "confidence": p.confidence,
        "common_hazard": p.common_hazard,
        "common_control_failure": p.common_control_failure,
        "potential_consequence": p.potential_consequence,
        "first_seen": p.first_seen.isoformat() if p.first_seen else None,
        "last_seen": p.last_seen.isoformat() if p.last_seen else None,
    }


@router.get("")
def list_patterns(
    db: Session = Depends(get_db),
    trend: str | None = None,
    sif_risk_level: str | None = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
):
    q = db.query(PatternCluster)
    if trend:
        q = q.filter(PatternCluster.trend == trend)
    patterns = q.order_by(PatternCluster.sif_score.desc()).all()

    results = [_pattern_summary(p) for p in patterns]
    if sif_risk_level:
        results = [r for r in results if r["sif_risk_level"] == sif_risk_level]

    total = len(results)
    start = (page - 1) * size
    paged = results[start:start + size]
    return {"patterns": paged, "total": total, "page": page, "size": size}


@router.get("/radar")
def emerging_radar(db: Session = Depends(get_db)):
    """Top emerging/increasing patterns for the dashboard radar widget."""
    patterns = db.query(PatternCluster).order_by(PatternCluster.sif_score.desc()).limit(8).all()
    return [{
        "id": p.id,
        "title": p.title,
        "trend": p.trend,
        "trend_pct": p.trend_pct,
        "sif_score": p.sif_score,
        "report_count": p.report_count,
    } for p in patterns]


@router.get("/{pattern_id}")
def get_pattern(pattern_id: str, db: Session = Depends(get_db)):
    p = db.query(PatternCluster).filter_by(id=pattern_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Pattern not found")

    links = db.query(ReportPatternLink).filter_by(pattern_id=pattern_id).all()
    related_reports = []
    for link in links:
        r = link.report
        related_reports.append({
            "id": r.id,
            "title": r.description[:100],
            "description": r.description,
            "report_date": r.report_date.isoformat() if r.report_date else None,
            "location": r.location,
            "contractor": r.contractor,
            "sif_score": r.assessment.overall_sif_score if r.assessment else None,
            "risk_level": r.assessment.risk_level if r.assessment else None,
            "similarity": round(link.similarity, 2),
        })
    related_reports.sort(key=lambda x: x["report_date"] or "", reverse=True)

    trend_chart_data = [{"month": k, "count": v} for k, v in sorted((p.monthly_counts or {}).items())]

    actions = [{
        "id": a.id, "priority": a.priority, "action": a.action,
        "rationale": a.rationale, "evidence_count": a.evidence_count, "status": a.status,
    } for a in p.actions]

    evidence_snippets = []
    for link in links[:6]:
        ext = link.report.extraction
        if ext and ext.evidence_spans:
            evidence_snippets.append({"report_id": link.report.id, "snippets": ext.evidence_spans})

    return {
        "pattern": _pattern_summary(p),
        "trend_chart_data": trend_chart_data,
        "related_reports": related_reports,
        "recommendations": actions,
        "evidence": evidence_snippets,
    }
