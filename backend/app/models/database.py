import uuid
import datetime as dt
from sqlalchemy import (
    Column, String, Float, Integer, Boolean, Text, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import declarative_base, relationship
try:
    from pgvector.sqlalchemy import Vector
except ImportError:
    Vector = None

Base = declarative_base()


def gen_id():
    return str(uuid.uuid4())


def now():
    return dt.datetime.utcnow()


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=gen_id)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    role = Column(String, default="officer")  # admin, manager, officer
    created_at = Column(DateTime, default=now)


class SafetyReport(Base):
    __tablename__ = "safety_reports"
    id = Column(String, primary_key=True, default=gen_id)
    report_date = Column(DateTime, nullable=False)
    report_type = Column(String, nullable=False)  # UNSAFE_ACT, UNSAFE_CONDITION, NEAR_MISS, INCIDENT
    location = Column(String)
    site = Column(String)
    department = Column(String)
    contractor = Column(String)
    reporter_role = Column(String)
    description = Column(Text, nullable=False)
    severity = Column(String, default="UNKNOWN")
    is_synthetic = Column(Boolean, default=True)
    planted_pattern = Column(String, nullable=True)  # for demo traceability only
    # Provenance from the data adapter layer (SIH26165 Phase 2): synthetic |
    # osha | niosh | oil | manual. Nullable/defaulted so it's backward
    # compatible with rows created before this column existed.
    source_system = Column(String, default="manual", nullable=True)
    created_at = Column(DateTime, default=now)
    
    # Sentence Transformer embedding (all-MiniLM-L6-v2 outputs 384-dimensional vectors)
    if Vector is not None:
        embedding = Column(Vector(384))
    else:
        embedding = Column(JSON) # Fallback if pgvector not installed

    extraction = relationship("SafetyExtraction", back_populates="report", uselist=False)
    assessment = relationship("SIFAssessment", back_populates="report", uselist=False)
    pattern_links = relationship("ReportPatternLink", back_populates="report")


class SafetyExtraction(Base):
    __tablename__ = "safety_extractions"
    id = Column(String, primary_key=True, default=gen_id)
    report_id = Column(String, ForeignKey("safety_reports.id"), nullable=False)
    activity = Column(String)
    hazard = Column(String)
    hazard_category = Column(String)
    unsafe_act = Column(String)
    unsafe_condition = Column(String)
    control_failure = Column(String)
    equipment = Column(String)
    location = Column(String)
    potential_consequence = Column(String)
    exposure_context = Column(String)
    sif_relevance_score = Column(Float)
    extraction_confidence = Column(Float)
    extraction_method = Column(String, default="rule_based")  # rule_based | llm
    evidence_spans = Column(JSON, default=list)  # sentence snippets that triggered extraction
    extracted_at = Column(DateTime, default=now)

    report = relationship("SafetyReport", back_populates="extraction")


class SIFAssessment(Base):
    __tablename__ = "sif_assessments"
    id = Column(String, primary_key=True, default=gen_id)
    report_id = Column(String, ForeignKey("safety_reports.id"), nullable=False)
    severity_score = Column(Float)
    exposure_score = Column(Float)
    control_failure_score = Column(Float)
    recurrence_score = Column(Float)
    consequence_score = Column(Float)
    overall_sif_score = Column(Float)
    risk_level = Column(String)  # CRITICAL, HIGH, MODERATE, LOW (continuous risk tier —
                                  # NOT the same concept as sif_label below; see canonical_schema.py docstring)
    reasoning = Column(JSON, default=list)  # list of "why flagged" bullet strings
    # Forward-compatible fields for Phase 4 (SIF classifier) and Phase 6
    # (Life-Saving Rule multi-label classifier). Nullable/empty until those
    # phases are implemented — an adapter MAY populate sif_label directly
    # if the source data already carries an expert/HSE-reviewed label.
    sif_label = Column(String, nullable=True)          # SIF | NON_SIF | UNCERTAIN
    sif_confidence = Column(Float, nullable=True)
    life_saving_rules = Column(JSON, default=list)      # list of IOGP Life-Saving Rule names, multi-label
    assessed_at = Column(DateTime, default=now)

    report = relationship("SafetyReport", back_populates="assessment")


class PatternCluster(Base):
    __tablename__ = "pattern_clusters"
    id = Column(String, primary_key=True, default=gen_id)
    title = Column(String)
    description = Column(Text)
    report_count = Column(Integer, default=0)
    locations = Column(JSON, default=list)
    contractors = Column(JSON, default=list)
    departments = Column(JSON, default=list)
    first_seen = Column(DateTime)
    last_seen = Column(DateTime)
    trend = Column(String)  # increasing, decreasing, stable, new
    trend_pct = Column(Float, default=0.0)
    sif_score = Column(Float)
    confidence = Column(Float)
    common_hazard = Column(String)
    common_control_failure = Column(String)
    potential_consequence = Column(String)
    monthly_counts = Column(JSON, default=dict)
    created_at = Column(DateTime, default=now)

    links = relationship("ReportPatternLink", back_populates="pattern")
    actions = relationship("RecommendedAction", back_populates="pattern")


class ReportPatternLink(Base):
    __tablename__ = "report_pattern_links"
    id = Column(String, primary_key=True, default=gen_id)
    report_id = Column(String, ForeignKey("safety_reports.id"))
    pattern_id = Column(String, ForeignKey("pattern_clusters.id"))
    similarity = Column(Float, default=0.0)

    report = relationship("SafetyReport", back_populates="pattern_links")
    pattern = relationship("PatternCluster", back_populates="links")


class RecommendedAction(Base):
    __tablename__ = "recommended_actions"
    id = Column(String, primary_key=True, default=gen_id)
    pattern_id = Column(String, ForeignKey("pattern_clusters.id"))
    priority = Column(String)  # CRITICAL, HIGH, MODERATE, LOW
    action = Column(Text)
    rationale = Column(Text)
    evidence_count = Column(Integer, default=0)
    status = Column(String, default="OPEN")
    created_at = Column(DateTime, default=now)

    pattern = relationship("PatternCluster", back_populates="actions")


class Annotation(Base):
    """Human-reviewed label for a report (SIH26165 Phase 13).

    A report may accumulate multiple annotations over time (re-review,
    disagreement, a second reviewer). Training (see app/ml/train.py) uses
    the most recent annotation per report_id — inter-annotator agreement /
    consensus resolution is intentionally out of scope for this v1; treat
    it as a known follow-up, not a hidden assumption.
    """
    __tablename__ = "annotations"
    id = Column(String, primary_key=True, default=gen_id)
    report_id = Column(String, ForeignKey("safety_reports.id"), nullable=False)
    annotator = Column(String, nullable=False)  # username, from the JWT
    sif_label = Column(String, nullable=False)  # SIF | NON_SIF | UNCERTAIN — required, unlike the
                                                  # classifier-populated field of the same name on
                                                  # SIFAssessment, which is a prediction, not a label
    life_saving_rules = Column(JSON, default=list)
    activity = Column(String, nullable=True)
    hazard = Column(String, nullable=True)
    unsafe_act = Column(String, nullable=True)
    unsafe_condition = Column(String, nullable=True)
    barrier_failure = Column(String, nullable=True)
    potential_consequence = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=now)

    report = relationship("SafetyReport")
