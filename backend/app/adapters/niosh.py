"""
Adapter for NIOSH FACE (Fatality Assessment and Control Evaluation) program
report extracts. NIOSH publishes FACE reports as narrative PDFs rather than
a single clean tabular export, so this adapter targets a *tabularized*
extract (report_id, narrative/abstract text, date, state, industry, etc.) —
whether produced by scraping NIOSH's report index or a third-party mirror.

Because every FACE report is, by definition, a fatality investigation, we
map report_type to INCIDENT unconditionally and leave severity as FATAL.
As with the OSHA adapter, SIF label / Life-Saving Rule fields are left for
the downstream classification pipeline — this adapter only normalizes shape.
"""
import datetime as dt
from typing import Optional

from app.adapters.base import SourceAdapter
from app.core.canonical_schema import CanonicalSafetyReport


class NioshAdapter(SourceAdapter):
    source_name = "niosh"

    default_column_mapping = {
        "report_text": "abstract",
        "date": "incident_date",
        "site": "state",
        "activity": "industry",
        "hazard": "keywords",
    }

    def _adapt_one(self, row: dict, mapping: dict[str, str]) -> Optional[CanonicalSafetyReport]:
        text = (self._get(row, mapping, "report_text") or "").strip()
        if not text:
            return None

        parsed_date = None
        date_val = self._get(row, mapping, "date")
        if date_val:
            for fmt in ("%Y-%m-%d", "%m/%d/%Y"):
                try:
                    parsed_date = dt.datetime.strptime(str(date_val), fmt)
                    break
                except ValueError:
                    continue

        return CanonicalSafetyReport(
            report_text=text,
            report_type="INCIDENT",
            date=parsed_date,
            site=self._get(row, mapping, "site"),
            activity=self._get(row, mapping, "activity"),
            hazard=self._get(row, mapping, "hazard"),
            severity="FATAL",
            source_system="niosh",
            raw=row,
        )
