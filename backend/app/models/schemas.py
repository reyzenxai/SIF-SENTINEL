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


class Config:
    orm_mode = True
