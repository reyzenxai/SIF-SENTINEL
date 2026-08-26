from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import CORS_ORIGINS
from app.db.session import init_db, SessionLocal
from app.api.v1.routers import api_router
from app.api.v1.endpoints.auth import seed_demo_users

app = FastAPI(title="SIF Sentinel API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
def on_startup():
    init_db()
    db = SessionLocal()
    try:
        seed_demo_users(db)
    finally:
        db.close()


@app.get("/")
def root():
    return {
        "name": "SIF Sentinel API",
        "status": "ok",
        "note": "Prototype demonstration uses synthetic/anonymized safety-report data. "
                "Production deployment would require authorized OIL data.",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}
