"""
Adapter for OIL India Limited's official Unsafe-Act/Unsafe-Condition/
Near-Miss/Incident export (SIH26165 — "OIL official data preparation").

This is the adapter the whole "plug-and-play" requirement hinges on. It
deliberately contains ZERO hardcoded OIL column names, labels, file
formats, or taxonomy assumptions in code. All of that lives in
oil_column_mapping.json (or an override passed at upload time), so when
OIL actually hands over real data:

  1. If their columns match the current mapping file: nothing changes.
  2. If they don't: edit oil_column_mapping.json (or pass a mapping
     override on the upload request) — no code change, no redeploy logic.

If OIL's data is unlabelled (no SIF/Life-Saving-Rule columns), those
fields simply come back None from the mapping lookup and the report flows
into the annotation workflow (Phase 13) instead of arriving pre-labelled.
"""
import datetime as dt
import json
from pathlib import Path
from typing import Optional

from app.adapters.base import SourceAdapter
from app.core.canonical_schema import CanonicalSafetyReport
from app.core.config import OIL_COLUMN_MAPPING_PATH


def load_default_oil_mapping() -> dict[str, str]:
    """Load the editable OIL column mapping from disk. Any key starting with
    '_' (like '_readme') is metadata, not a field mapping, and is dropped."""
    path = Path(OIL_COLUMN_MAPPING_PATH)
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return {k: v for k, v in raw.items() if not k.startswith("_")}


class OilAdapter(SourceAdapter):
    source_name = "oil"

    def __init__(self):
        # Loaded fresh at construction so editing the JSON file and
        # restarting the API (or re-registering the adapter) is enough to
        # pick up new column names — no code deploy needed.
        self.default_column_mapping = load_default_oil_mapping()

    def _adapt_one(self, row: dict, mapping: dict[str, str]) -> Optional[CanonicalSafetyReport]:
        text = (self._get(row, mapping, "report_text") or "").strip()
        if not text:
            return None

        parsed_date = None
        date_val = self._get(row, mapping, "date")
        if date_val:
            if isinstance(date_val, dt.datetime):
                parsed_date = date_val
            else:
                for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d %H:%M:%S"):
                    try:
                        parsed_date = dt.datetime.strptime(str(date_val), fmt)
                        break
                    except ValueError:
                        continue

        lsr_raw = self._get(row, mapping, "life_saving_rules")
        if isinstance(lsr_raw, str) and lsr_raw:
            life_saving_rules = [r.strip() for r in lsr_raw.split(",") if r.strip()]
        elif isinstance(lsr_raw, list):
            life_saving_rules = lsr_raw
        else:
            life_saving_rules = []

        return CanonicalSafetyReport(
            report_text=text,
            report_type=self._get(row, mapping, "report_type"),
            date=parsed_date,
            site=self._get(row, mapping, "site"),
            location=self._get(row, mapping, "location"),
            activity=self._get(row, mapping, "activity"),
            hazard=self._get(row, mapping, "hazard"),
            unsafe_act=self._get(row, mapping, "unsafe_act"),
            unsafe_condition=self._get(row, mapping, "unsafe_condition"),
            barrier_failure=self._get(row, mapping, "barrier_failure"),
            potential_consequence=self._get(row, mapping, "potential_consequence"),
            severity=self._get(row, mapping, "severity"),
            department=self._get(row, mapping, "department"),
            contractor=self._get(row, mapping, "contractor"),
            reporter_role=self._get(row, mapping, "reporter_role"),
            sif_label=self._get(row, mapping, "sif_label"),  # None unless OIL pre-labelled
            life_saving_rules=life_saving_rules,
            source_system="oil",
            raw=row,
        )
