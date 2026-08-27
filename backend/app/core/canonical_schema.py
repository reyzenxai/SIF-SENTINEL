"""
Canonical Safety Report Schema (SIH26165 — Phase 2).

This is the single normalized shape every data source (OSHA, NIOSH,
synthetic, and eventually OIL's official export) is converted into before
it touches the ML/NLP pipeline, the risk engine, or the database.

Adapters (see app/adapters/) are the ONLY place that should know about a
source's original column names. Everything downstream speaks this schema
and nothing else. If a source has data this schema can't represent, that's
a signal the adapter should drop it into `raw` for audit purposes rather
than this class growing source-specific fields.

Field names intentionally match the SIH26165 brief's canonical schema list:
report_id, report_text, report_type, date, site, location, activity,
hazard, unsafe_act, unsafe_condition, barrier_failure, exposure,
potential_consequence, sif_label, sif_confidence, life_saving_rules, severity.
"""
import datetime as dt
import uuid
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ReportType(str, Enum):
    UA = "UA"                 # Unsafe Act
    UC = "UC"                 # Unsafe Condition
    NEAR_MISS = "NEAR_MISS"
    INCIDENT = "INCIDENT"


class SIFLabel(str, Enum):
    SIF = "SIF"
    NON_SIF = "NON_SIF"
    UNCERTAIN = "UNCERTAIN"   # intentional: forces human HSE review instead of
                               # a forced binary call on a safety-critical decision


# Aliases seen across sources / earlier project conventions, normalized onto
# the canonical ReportType. Extend this list — don't invent parallel enums
# elsewhere in the codebase for the same concept.
_REPORT_TYPE_ALIASES = {
    "unsafe_act": ReportType.UA, "unsafe act": ReportType.UA, "ua": ReportType.UA,
    "unsafe_condition": ReportType.UC, "unsafe condition": ReportType.UC, "uc": ReportType.UC,
    "near_miss": ReportType.NEAR_MISS, "near miss": ReportType.NEAR_MISS,
    "nearmiss": ReportType.NEAR_MISS, "near-miss": ReportType.NEAR_MISS,
    "incident": ReportType.INCIDENT, "accident": ReportType.INCIDENT, "injury": ReportType.INCIDENT,
}


def normalize_report_type(value) -> ReportType:
    """Best-effort normalization of a source's report-type text into the
    canonical enum. Unknown/blank values default to NEAR_MISS (the safest
    default: still gets analyzed, never silently dropped)."""
    if value is None or (isinstance(value, str) and not value.strip()):
        return ReportType.NEAR_MISS
    if isinstance(value, ReportType):
        return value
    key = str(value).strip().lower()
    if key in _REPORT_TYPE_ALIASES:
        return _REPORT_TYPE_ALIASES[key]
    try:
        return ReportType(str(value).strip().upper())
    except ValueError:
        return ReportType.NEAR_MISS


# Legacy DB values (see app/models/database.py) are long-form and predate
# this schema. Mapping here means the existing DB/frontend does not need to
# change to accept new sources.
_TO_LEGACY_REPORT_TYPE = {
    ReportType.UA: "UNSAFE_ACT",
    ReportType.UC: "UNSAFE_CONDITION",
    ReportType.NEAR_MISS: "NEAR_MISS",
    ReportType.INCIDENT: "INCIDENT",
}


class CanonicalSafetyReport(BaseModel):
    """The canonical internal schema every ingested report is converted to."""

    report_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    report_text: str
    report_type: ReportType = ReportType.NEAR_MISS
    date: Optional[dt.datetime] = None
    site: Optional[str] = None
    location: Optional[str] = None

    # Structured precursor fields. Usually populated downstream by the
    # extraction pipeline (Phase 5), but an adapter MAY pre-populate these if
    # the source already carries expert-annotated data (e.g. an OIL export
    # that already has HSE-reviewed fields, or a hand-labelled batch).
    activity: Optional[str] = None
    hazard: Optional[str] = None
    unsafe_act: Optional[str] = None
    unsafe_condition: Optional[str] = None
    barrier_failure: Optional[str] = None
    exposure: Optional[str] = None
    potential_consequence: Optional[str] = None

    # SIF classification fields. UNCERTAIN is a first-class value, not an
    # error state — see SIFLabel docstring. Populated by Phase 4's
    # classifier; adapters leave these None unless the source is pre-labelled.
    sif_label: Optional[SIFLabel] = None
    sif_confidence: Optional[float] = None
    life_saving_rules: list[str] = Field(default_factory=list)
    severity: Optional[str] = None

    # Provenance fields. Not in the brief's literal field list, but required
    # so that once multiple sources are merged we can always answer "is this
    # actually OIL data or synthetic/public data" — the brief is explicit
    # that we must never blur that line.
    source_system: str = "unknown"          # synthetic | osha | niosh | oil | manual
    department: Optional[str] = None
    contractor: Optional[str] = None
    reporter_role: Optional[str] = None
    raw: dict = Field(default_factory=dict)  # original row, kept for audit/debugging

    @field_validator("report_type", mode="before")
    @classmethod
    def _norm_type(cls, v):
        return normalize_report_type(v)

    @field_validator("sif_label", mode="before")
    @classmethod
    def _norm_sif_label(cls, v):
        if v is None or (isinstance(v, str) and not v.strip()):
            return None
        if isinstance(v, SIFLabel):
            return v
        key = str(v).strip().upper().replace("-", "_").replace(" ", "_")
        if key in ("NON_SIF", "NONSIF", "NOT_SIF"):
            return SIFLabel.NON_SIF
        if key in ("SIF",):
            return SIFLabel.SIF
        return SIFLabel.UNCERTAIN

    def to_legacy_ingest_dict(self) -> dict:
        """Bridge to the existing pipeline.ingest_report() contract so the
        current ML pipeline (extraction -> risk engine -> clustering) does
        not need to change in order to consume new sources. This is the
        ONE place canonical -> legacy field-name translation happens."""
        return {
            "report_date": self.date or dt.datetime.utcnow(),
            "report_type": _TO_LEGACY_REPORT_TYPE[self.report_type],
            "location": self.location,
            "site": self.site or self.location,
            "department": self.department,
            "contractor": self.contractor,
            "reporter_role": self.reporter_role,
            "description": self.report_text,
            "severity": self.severity or "UNKNOWN",
            "planted_pattern": None,
            "source_system": self.source_system,
        }
