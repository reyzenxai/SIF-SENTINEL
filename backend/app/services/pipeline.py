"""Orchestrates the full pipeline: ingest -> extract -> assess -> cluster -> act."""
import datetime as dt
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.database import (
    SafetyReport, SafetyExtraction, SIFAssessment, PatternCluster,
    ReportPatternLink, RecommendedAction
)
from app.services import extraction_service, risk_engine, pattern_engine, action_engine
from app.ml import predict_service as sif_classifier


def ingest_report(db: Session, report_data: dict, is_synthetic=True) -> SafetyReport:
    report = SafetyReport(
        report_date=report_data.get("report_date") or dt.datetime.utcnow(),
        report_type=report_data.get("report_type", "NEAR_MISS"),
        location=report_data.get("location"),
        site=report_data.get("site") or report_data.get("location"),
        department=report_data.get("department"),
        contractor=report_data.get("contractor"),
        reporter_role=report_data.get("reporter_role"),
        description=report_data["description"],
        severity=report_data.get("severity", "UNKNOWN"),
        is_synthetic=is_synthetic,
        planted_pattern=report_data.get("planted_pattern"),
        source_system=report_data.get("source_system", "manual"),
    )
    db.add(report)
    db.flush()
    return report


def extract_and_assess_report(db: Session, report: SafetyReport, similar_count: int = 0):
    extraction_result = extraction_service.extract(report.description)

    extraction = SafetyExtraction(
        report_id=report.id,
        activity=extraction_result.get("activity"),
        hazard=extraction_result.get("hazard"),
        hazard_category=extraction_result.get("hazard_category"),
        unsafe_act=extraction_result.get("unsafe_act"),
        unsafe_condition=extraction_result.get("unsafe_condition"),
        control_failure=extraction_result.get("control_failure"),
        equipment=extraction_result.get("equipment"),
        location=report.location,
        potential_consequence=extraction_result.get("potential_consequence"),
        exposure_context=extraction_result.get("exposure_context"),
        sif_relevance_score=extraction_result.get("sif_relevance_score"),
        extraction_confidence=extraction_result.get("extraction_confidence"),
        extraction_method=extraction_result.get("extraction_method", "rule_based"),
        evidence_spans=extraction_result.get("evidence_spans", []),
    )
    db.add(extraction)
    db.flush()

    assessment_result = risk_engine.assess(extraction_result, similar_report_count=similar_count)
    sif_prediction = sif_classifier.predict(report.description)  # None until a model is trained (Phase 4)
    assessment = SIFAssessment(
        report_id=report.id,
        severity_score=assessment_result["severity_score"],
        exposure_score=assessment_result["exposure_score"],
        control_failure_score=assessment_result["control_failure_score"],
        recurrence_score=assessment_result["recurrence_score"],
        consequence_score=assessment_result["overall_sif_score"] and assessment_result["consequence_score"],
        overall_sif_score=assessment_result["overall_sif_score"],
        risk_level=assessment_result["risk_level"],
        reasoning=assessment_result["reasoning"],
        sif_label=sif_prediction.sif_label if sif_prediction else None,
        sif_confidence=sif_prediction.sif_probability if sif_prediction else None,
    )
    db.add(assessment)
    db.flush()
    return extraction, assessment


def run_full_pipeline(db: Session, reports_data: list[dict], is_synthetic=True, progress_every=200):
    """Bulk ingest + extract + assess (recurrence computed post-clustering), then cluster + generate actions."""
    reports = []
    for i, rd in enumerate(reports_data):
        report = ingest_report(db, rd, is_synthetic=is_synthetic)
        reports.append(report)
    db.commit()

    # First pass extraction (recurrence unknown yet -> 0)
    for report in reports:
        extract_and_assess_report(db, report, similar_count=0)
    db.commit()

    # Pattern discovery
    cluster_input = []
    for report in reports:
        ext = db.query(SafetyExtraction).filter_by(report_id=report.id).first()
        cluster_input.append({
            "id": report.id,
            "description": report.description,
            "report_date": report.report_date,
            "location": report.location,
            "contractor": report.contractor,
            "department": report.department,
            "hazard_category": ext.hazard_category if ext else None,
            "control_failure": ext.control_failure if ext else None,
            "potential_consequence": ext.potential_consequence if ext else None,
        })

    clusters = pattern_engine.cluster_reports(cluster_input)

    id_to_report = {r.id: r for r in reports}

    for label, cluster_data in clusters.items():
        member_reports = cluster_data["reports"]
        confidence = cluster_data["confidence"]
        summary = pattern_engine.summarize_cluster(member_reports)

        # crude SIF score for the pattern: average of member assessments, boosted by recurrence
        member_ids = [r["id"] for r in member_reports]
        avg_score = db.query(func.avg(SIFAssessment.overall_sif_score)).join(
            SafetyReport, SafetyReport.id == SIFAssessment.report_id
        ).filter(SafetyReport.id.in_(member_ids)).scalar() or 0
        recurrence_boost = min(len(member_ids) * 0.8, 20)
        pattern_sif_score = round(min(avg_score + recurrence_boost, 100), 1)

        pattern = PatternCluster(
            title=summary["title"],
            description=summary["description"],
            report_count=summary["report_count"],
            locations=summary["locations"],
            contractors=summary["contractors"],
            departments=summary["departments"],
            first_seen=summary["first_seen"],
            last_seen=summary["last_seen"],
            trend=summary["trend"],
            trend_pct=summary["trend_pct"],
            sif_score=pattern_sif_score,
            confidence=confidence,
            common_hazard=summary["common_hazard"],
            common_control_failure=summary["common_control_failure"],
            potential_consequence=summary["potential_consequence"],
            monthly_counts=summary["monthly_counts"],
        )
        db.add(pattern)
        db.flush()

        for r in member_reports:
            db.add(ReportPatternLink(report_id=r["id"], pattern_id=pattern.id, similarity=confidence))

        # Update recurrence-aware SIF assessment for member reports
        for r in member_reports:
            report_obj = id_to_report[r["id"]]
            assessment = db.query(SIFAssessment).filter_by(report_id=report_obj.id).first()
            if assessment:
                new_recurrence = risk_engine.compute_recurrence(len(member_ids))
                new_total = round(
                    assessment.severity_score + assessment.control_failure_score +
                    assessment.exposure_score + new_recurrence + assessment.consequence_score, 1
                )
                new_total = min(new_total, 100.0)
                assessment.recurrence_score = round(new_recurrence, 1)
                assessment.overall_sif_score = new_total
                assessment.risk_level = risk_engine.risk_level_for_score(new_total)
                if f"Similar events repeated {len(member_ids)} times" not in assessment.reasoning:
                    reasoning = list(assessment.reasoning or [])
                    reasoning.append(f"Similar events repeated {len(member_ids)} times across the '{pattern.title}' pattern")
                    reasoning.append(f"Frequency trend: {pattern.trend} ({pattern.trend_pct:+.1f}% vs prior period)")
                    assessment.reasoning = reasoning

        # Action engine
        pattern_summary_for_actions = {
            "common_hazard": summary["common_hazard"],
            "sif_score": pattern_sif_score,
            "report_count": summary["report_count"],
            "trend": summary["trend"],
        }
        actions = action_engine.generate_actions(pattern_summary_for_actions)
        for a in actions:
            db.add(RecommendedAction(
                pattern_id=pattern.id,
                priority=a["priority"],
                action=a["action"],
                rationale=a["rationale"],
                evidence_count=a["evidence_count"],
            ))

    db.commit()
    return {
        "reports_ingested": len(reports),
        "patterns_discovered": len(clusters),
    }
