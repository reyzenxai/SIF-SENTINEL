import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Swap to Postgres for deployment
DATABASE_URL = os.environ.get(
    "DATABASE_URL", 
    "postgresql+psycopg2://user:password@localhost/sifsentinel"
)

# Optional LLM extraction. If neither key is present, the system uses the
# deterministic rule-based/ontology extraction pipeline (SIH brief section 11 & 32).
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
LLM_ENABLED = bool(ANTHROPIC_API_KEY or OPENAI_API_KEY)

JWT_SECRET = os.environ.get("JWT_SECRET", "sif-sentinel-dev-secret-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60 * 12

# Prototype methodology — configurable for OIL's approved safety framework.
SIF_SCORE_WEIGHTS = {
    "severity": 25,
    "control_failure": 25,
    "exposure": 20,
    "recurrence": 20,
    "consequence": 10,
}

CLUSTER_MIN_SAMPLES = 3
CLUSTER_EPS = 0.55  # cosine-distance DBSCAN epsilon over TF-IDF vectors

CORS_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]
