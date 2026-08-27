"""API endpoints for the SIF classifier model registry (SIH26165 — Phase 4)."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_user
from app.ml import registry, train as train_module

router = APIRouter()


class TrainRequest(BaseModel):
    model_type: str = "tfidf_logreg"
    activate: bool = True
    eval_fraction: float = 0.2
    label_source: str = "auto"  # auto | annotated | weak_bootstrap — see app/ml/train.py


@router.get("/models")
def list_models(current_user: dict = Depends(get_current_user)):
    """List every trained SIF classifier with its metrics and label source."""
    return {"models": registry.list_models()}


@router.get("/active")
def get_active_model(current_user: dict = Depends(get_current_user)):
    """The model currently used for inference in the report pipeline, or
    null if none has been trained/activated yet."""
    entry = registry.get_active_entry()
    return {"active_model": entry}


@router.post("/train")
def train_model(
    body: TrainRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Train a baseline SIF classifier (TF-IDF + Logistic Regression or
    XGBoost) on the reports currently in the database, using the weak-label
    bootstrap documented in app/ml/labeling.py — NOT real ground truth. See
    that module's docstring before trusting these numbers as real accuracy.
    """
    try:
        entry = train_module.train_and_register(
            db, model_type=body.model_type, activate=body.activate,
            eval_fraction=body.eval_fraction, label_source=body.label_source,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"message": "Model trained.", "model": entry}


@router.post("/activate/{model_version}")
def activate_model(model_version: str, current_user: dict = Depends(get_current_user)):
    try:
        entry = registry.set_active(model_version)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return {"message": "Model activated.", "model": entry}
