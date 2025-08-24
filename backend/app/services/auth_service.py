import hashlib
from sqlalchemy.orm import Session
from app.db.base import SessionLocal
from app.db.models.user import User

def sha1_hash(password: str) -> str:
    return hashlib.sha1(password.encode()).hexdigest()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def register(db: Session, username: str, password: str):
    if db.query(User).filter(User.username == username).first():
        return None
    user = User(username=username, password_sha1=sha1_hash(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"username": user.username}

def login(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if user.password_sha1 == sha1_hash(password):
        return {"username": user.username}
    return None