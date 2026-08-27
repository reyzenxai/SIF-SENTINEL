import datetime as dt
from typing import Optional, List, Any
from pydantic import BaseModel


class ReportIn(BaseModel):
    description: str
    report_type: str = "NEAR_MISS"
    location: Optional[str] = None
    site: Optional[str] = None
    department: Optional[str] = None
    contractor: Optional[str] = None
    reporter_role: Optional[str] = None
    report_date: Optional[dt.datetime] = None


class LoginIn(BaseModel):
    username: str
    password: str


class AnnotationIn(BaseModel):
    """SIH26165 Phase 13: a human HSE reviewer's label for a report."""
    sif_label: str  # SIF | NON_SIF | UNCERTAIN
    life_saving_rules: List[str] = []
    activity: Optional[str] = None
    hazard: Optional[str] = None
    unsafe_act: Optional[str] = None
    unsafe_condition: Optional[str] = None
    barrier_failure: Optional[str] = None
    potential_consequence: Optional[str] = None
    notes: Optional[str] = None


class Config:
    orm_mode = True
