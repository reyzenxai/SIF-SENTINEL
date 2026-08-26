from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.database import User
from app.models.schemas import LoginIn
from app.core.security import create_token, hash_password, verify_password

router = APIRouter()

DEMO_USERS = [
    {"username": "safety.manager", "password": "demo1234", "role": "manager", "email": "safety.manager@example.com"},
    {"username": "site.officer", "password": "demo1234", "role": "officer", "email": "site.officer@example.com"},
    {"username": "admin", "password": "demo1234", "role": "admin", "email": "admin@example.com"},
]


def seed_demo_users(db: Session):
    for u in DEMO_USERS:
        existing = db.query(User).filter_by(username=u["username"]).first()
        if not existing:
            db.add(User(username=u["username"], hashed_password=hash_password(u["password"]),
                         email=u["email"], role=u["role"]))
    db.commit()


@router.post("/login")
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(username=body.username).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_token({"sub": user.id, "username": user.username, "role": user.role})
    return {"access_token": token, "token_type": "bearer", "role": user.role, "username": user.username}


@router.get("/demo-credentials")
def demo_credentials():
    """Prototype convenience endpoint listing demo login credentials."""
    return [{"username": u["username"], "password": u["password"], "role": u["role"]} for u in DEMO_USERS]
