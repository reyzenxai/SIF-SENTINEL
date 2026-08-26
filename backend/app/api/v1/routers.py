from fastapi import APIRouter
from app.api.v1.endpoints import auth, reports, patterns, dashboard, ontology, demo

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(patterns.router, prefix="/patterns", tags=["patterns"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(ontology.router, prefix="/ontology", tags=["ontology"])
api_router.include_router(demo.router, prefix="/demo", tags=["demo"])
