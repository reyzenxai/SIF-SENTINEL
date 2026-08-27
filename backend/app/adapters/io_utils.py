"""
File parsing utilities for adapter ingestion.

Deliberately dumb: turns bytes into a list of plain dict rows regardless of
whether the source file is CSV, Excel, or JSON. Column-name mapping and
canonicalization happen later, inside an adapter. Keeping this step
format-only means adapters never need to know or care what file format the
data arrived in.
"""
import csv
import io
import json

import pandas as pd


def parse_upload(filename: str, raw_bytes: bytes) -> list[dict]:
    """Parse an uploaded file's bytes into a list of dict rows.

    Supports .xlsx/.xls, .json, and .csv (default fallback). Raises
    ValueError on content that cannot be parsed at all — callers should
    turn that into a 400 response.
    """
    name = (filename or "").lower()

    try:
        if name.endswith((".xlsx", ".xls")):
            df = pd.read_excel(io.BytesIO(raw_bytes))
            return df.where(pd.notnull(df), None).to_dict(orient="records")

        if name.endswith(".json"):
            data = json.loads(raw_bytes.decode("utf-8", errors="ignore"))
            if isinstance(data, dict):
                # tolerate common export shapes like {"reports": [...]}
                for key in ("reports", "data", "records", "rows"):
                    if key in data and isinstance(data[key], list):
                        return data[key]
                return [data]
            if isinstance(data, list):
                return data
            raise ValueError("JSON upload must be an object or a list of records")

        # default: CSV (also handles .txt/.tsv-ish exports reasonably)
        text = raw_bytes.decode("utf-8-sig", errors="ignore")
        reader = csv.DictReader(io.StringIO(text))
        rows = list(reader)
        if not rows:
            raise ValueError("Empty or malformed CSV")
        return rows
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError(f"Could not parse uploaded file: {exc}") from exc
