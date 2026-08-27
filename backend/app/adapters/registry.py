"""
Adapter registry (SIH26165 — Phase 2).

Single place new data sources get plugged in. To add a new source: write a
SourceAdapter subclass in this package, then add one line here. Nothing
else in the codebase (pipeline, endpoints, DB) needs to change.
"""
from app.adapters.base import SourceAdapter
from app.adapters.synthetic import SyntheticAdapter
from app.adapters.osha import OshaAdapter
from app.adapters.niosh import NioshAdapter
from app.adapters.oil import OilAdapter

_ADAPTERS: dict[str, SourceAdapter] = {
    "synthetic": SyntheticAdapter(),
    "osha": OshaAdapter(),
    "niosh": NioshAdapter(),
    "oil": OilAdapter(),
}


def get_adapter(source: str) -> SourceAdapter:
    key = (source or "").strip().lower()
    if key not in _ADAPTERS:
        raise ValueError(f"Unknown data source '{source}'. Available: {sorted(_ADAPTERS)}")
    return _ADAPTERS[key]


def available_sources() -> list[str]:
    return sorted(_ADAPTERS)
