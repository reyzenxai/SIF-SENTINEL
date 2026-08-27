"""
Adapter for OSHA's public Severe Injury Report (SIR) dataset
(https://www.osha.gov/severeinjury — "Severe Injury Reports" CSV export).

The default_column_mapping below matches OSHA's published export headers as
of this writing. OSHA has changed column names across export vintages
before, so this is a *default*, not an assumption baked into the parsing
logic — pass column_mapping overrides to adapt_rows() if a downloaded file
uses different headers, exactly like the OIL adapter.

OSHA SIRs have no SIF/NON-SIF label and no Life-Saving Rule mapping — those
fields are left None here and populated later by the classification/
extraction pipeline (Phases 4-6). Treat this data as public augmentation
only, never as a stand-in for OIL's own reports (see brief: "do not treat
synthetic/public data as ground truth").
"""
import datetime as dt
from typing import Optional

from app.adapters.base import SourceAdapter
from app.core.canonical_schema import CanonicalSafetyReport


class OshaAdapter(SourceAdapter):
    source_name = "osha"

    default_column_mapping = {
        "report_text": "Final Narrative",
        "date": "EventDate",
        "location": "City",
        "site": "State",
        "hazard": "NatureTitle",
        "activity": "SourceTitle",
        "potential_consequence": "PartOfBodyTitle",
    }

    def _adapt_one(self, row: dict, mapping: dict[str, str]) -> Optional[CanonicalSafetyReport]:
        text = (self._get(row, mapping, "report_text") or "").strip()
        if not text:
            return None

        parsed_date = None
        date_val = self._get(row, mapping, "date")
        if date_val:
            for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%Y %H:%M"):
                try:
                    parsed_date = dt.datetime.strptime(str(date_val), fmt)
                    break
                except ValueError:
                    continue

        city = self._get(row, mapping, "location")
        state = self._get(row, mapping, "site")
        location = ", ".join(p for p in [city, state] if p) or None

        return CanonicalSafetyReport(
            report_text=text,
            report_type="INCIDENT",  # OSHA SIRs are, by definition, actual severe injuries
            date=parsed_date,
            site=state,
            location=location,
            hazard=self._get(row, mapping, "hazard"),
            activity=self._get(row, mapping, "activity"),
            potential_consequence=self._get(row, mapping, "potential_consequence"),
            source_system="osha",
            raw=row,
        )
