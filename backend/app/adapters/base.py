"""
Data source adapter base class (SIH26165 — Phase 2).

An adapter's ONLY job is: take a source's raw rows (already parsed into
list[dict] by app/adapters/io_utils.py) plus a column mapping, and emit
CanonicalSafetyReport objects. Adapters must never touch the database, the
ML pipeline, or the risk engine directly — that coupling is exactly what
would make adding a new source (or updating OIL's column names) expensive.

To add a new source: subclass SourceAdapter, provide default_column_mapping
and _adapt_one(), then register it in app/adapters/registry.py. Nothing
else in the codebase should need to change.
"""
from abc import ABC, abstractmethod
from typing import Optional

from app.core.canonical_schema import CanonicalSafetyReport


class SourceAdapter(ABC):
    source_name: str = "unknown"

    #: Default column_name -> canonical_field mapping for this source.
    #: Callers can override/extend this per-request without touching code —
    #: this is what makes a source "plug-and-play" once real column headers
    #: are known (this matters most for the OIL adapter; see oil.py).
    default_column_mapping: dict[str, str] = {}

    def effective_mapping(self, override: Optional[dict[str, str]] = None) -> dict[str, str]:
        mapping = dict(self.default_column_mapping)
        if override:
            mapping.update(override)
        return mapping

    def adapt_rows(
        self, rows: list[dict], column_mapping: Optional[dict[str, str]] = None
    ) -> list[CanonicalSafetyReport]:
        mapping = self.effective_mapping(column_mapping)
        out = []
        for row in rows:
            canonical = self._adapt_one(row, mapping)
            if canonical is not None:
                out.append(canonical)
        return out

    @abstractmethod
    def _adapt_one(self, row: dict, mapping: dict[str, str]) -> Optional[CanonicalSafetyReport]:
        """Convert a single raw row into a CanonicalSafetyReport, or return
        None to skip it (e.g. the row has no usable report text)."""
        ...

    @staticmethod
    def _get(row: dict, mapping: dict[str, str], canonical_field: str, default=None):
        """Look up a canonical field's value in a raw row via the mapping,
        tolerating header case/whitespace drift — common in real-world
        exports (Excel columns get re-typed, extra spaces creep in, etc.)."""
        source_col = mapping.get(canonical_field)
        if not source_col:
            return default
        if source_col in row:
            val = row[source_col]
            return val if val not in (None, "") else default
        lowered = {str(k).strip().lower(): v for k, v in row.items()}
        val = lowered.get(str(source_col).strip().lower(), default)
        return val if val not in (None, "") else default
