from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.database import SafetyReport
from app.services import pipeline
from app.core.config import LLM_ENABLED
from synthetic_data.generate_data import generate as generate_synthetic

router = APIRouter()


@router.post("/seed")
def seed_synthetic_dataset(db: Session = Depends(get_db), n: int = 1000):
    """Generates and ingests the full synthetic demo dataset (spec section 27/28)."""
    existing_count = db.query(SafetyReport).count()
    if existing_count > 0:
        return {"message": "Dataset already seeded.", "existing_reports": existing_count}

    reports_data = generate_synthetic(n_total_target=n)
    result = pipeline.run_full_pipeline(db, reports_data, is_synthetic=True)
    return {
        "message": "Synthetic demo dataset generated and processed.",
        "reports_ingested": result["reports_ingested"],
        "patterns_discovered": result["patterns_discovered"],
        "llm_enabled": LLM_ENABLED,
    }


@router.get("/status")
def demo_status(db: Session = Depends(get_db)):
    count = db.query(SafetyReport).count()
    return {"reports_seeded": count, "llm_enabled": LLM_ENABLED}
