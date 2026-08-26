from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import get_db
from app.models.database import SafetyReport, SafetyExtraction, SIFAssessment, PatternCluster

router = APIRouter()


@router.get("/kpis")
def get_kpis(db: Session = Depends(get_db)):
    total_reports = db.query(func.count(SafetyReport.id)).scalar() or 0
    sif_precursors = db.query(func.count(SIFAssessment.id)).filter(
        SIFAssessment.risk_level.in_(["HIGH", "CRITICAL"])
    ).scalar() or 0
    critical_patterns = db.query(func.count(PatternCluster.id)).filter(PatternCluster.sif_score >= 80).scalar() or 0
    emerging_patterns = db.query(func.count(PatternCluster.id)).filter(
        PatternCluster.trend.in_(["increasing", "new"])
    ).scalar() or 0
    total_patterns = db.query(func.count(PatternCluster.id)).scalar() or 0

    high_risk_sites = db.query(SafetyReport.site, func.avg(SIFAssessment.overall_sif_score).label("avg_score")).join(
        SIFAssessment, SIFAssessment.report_id == SafetyReport.id
    ).group_by(SafetyReport.site).having(func.avg(SIFAssessment.overall_sif_score) >= 60).count()

    hazards_extracted = db.query(func.count(SafetyExtraction.id)).filter(
        SafetyExtraction.hazard_category.isnot(None)
    ).scalar() or 0
    control_failures = db.query(func.count(SafetyExtraction.id)).filter(
        SafetyExtraction.control_failure.isnot(None)
    ).scalar() or 0

    avg_score = db.query(func.avg(SIFAssessment.overall_sif_score)).scalar() or 0

    return {
        "total_reports": total_reports,
        "sif_precursors": sif_precursors,
        "critical_patterns": critical_patterns,
        "emerging_patterns": emerging_patterns,
        "total_patterns": total_patterns,
        "high_risk_sites": high_risk_sites,
        "hazards_extracted": hazards_extracted,
        "control_failures_detected": control_failures,
        "avg_sif_score": round(avg_score, 1),
    }


@router.get("/heatmap")
def get_heatmap(db: Session = Depends(get_db)):
    rows = db.query(
        SafetyReport.site,
        func.avg(SIFAssessment.overall_sif_score).label("avg_score"),
        func.count(SafetyReport.id).label("count"),
    ).join(SIFAssessment, SIFAssessment.report_id == SafetyReport.id).group_by(SafetyReport.site).all()

    def risk_level(score):
        if score >= 80:
            return "CRITICAL"
        if score >= 60:
            return "HIGH"
        if score >= 35:
            return "MODERATE"
        return "LOW"

    return [{
        "site": r.site,
        "score": round(r.avg_score, 1),
        "count": r.count,
        "risk_level": risk_level(r.avg_score),
    } for r in rows if r.site]


@router.get("/hazard-breakdown")
def hazard_breakdown(db: Session = Depends(get_db)):
    rows = db.query(
        SafetyExtraction.hazard_category, func.count(SafetyExtraction.id).label("count")
    ).filter(SafetyExtraction.hazard_category.isnot(None)).group_by(SafetyExtraction.hazard_category).all()
    return [{"hazard_category": r.hazard_category, "count": r.count} for r in rows]


@router.get("/contractor-analytics")
def contractor_analytics(db: Session = Depends(get_db)):
    rows = db.query(
        SafetyReport.contractor,
        func.count(SafetyReport.id).label("report_count"),
        func.avg(SIFAssessment.overall_sif_score).label("avg_score"),
    ).join(SIFAssessment, SIFAssessment.report_id == SafetyReport.id).group_by(
        SafetyReport.contractor
    ).order_by(func.avg(SIFAssessment.overall_sif_score).desc()).limit(15).all()

    return [{
        "contractor": r.contractor,
        "report_count": r.report_count,
        "avg_sif_score": round(r.avg_score, 1),
        "note": "Higher concentration of reports associated with selected precursor categories; targeted review recommended." if r.avg_score >= 60 else None,
    } for r in rows if r.contractor]
