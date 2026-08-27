"""
Adapter for SIF Sentinel's own synthetic dataset (synthetic_data/generate_data.py
output / backend/synthetic_data/samples/synthetic_reports.csv).

Column names already match the canonical fields closely — this adapter
exists mainly so "synthetic" is a first-class, explicitly-labelled source
alongside OSHA/NIOSH/OIL, rather than a special case baked into the upload
endpoint (which is what the previous /reports/upload did, and still does,
for backward compatibility).
"""
import datetime as dt
from typing import Optional

from app.adapters.base import SourceAdapter
from app.core.canonical_schema import CanonicalSafetyReport


class SyntheticAdapter(SourceAdapter):
    source_name = "synthetic"

    default_column_mapping = {
        "report_text": "description",
        "report_type": "report_type",
        "date": "report_date",
        "site": "site",
        "location": "location",
        "department": "department",
        "contractor": "contractor",
        "reporter_role": "reporter_role",
        "severity": "severity",
    }

    def _adapt_one(self, row: dict, mapping: dict[str, str]) -> Optional[CanonicalSafetyReport]:
        text = (self._get(row, mapping, "report_text") or "").strip()
        if not text:
            return None

        parsed_date = None
        date_val = self._get(row, mapping, "date")
        if date_val:
            try:
                parsed_date = dt.datetime.fromisoformat(str(date_val))
            except ValueError:
                parsed_date = None

        return CanonicalSafetyReport(
            report_text=text,
            report_type=self._get(row, mapping, "report_type"),
            date=parsed_date,
            site=self._get(row, mapping, "site"),
            location=self._get(row, mapping, "location"),
            department=self._get(row, mapping, "department"),
            contractor=self._get(row, mapping, "contractor"),
            reporter_role=self._get(row, mapping, "reporter_role"),
            severity=self._get(row, mapping, "severity"),
            source_system="synthetic",
            raw=row,
        )
