# app/db/models/user.py
from sqlalchemy import Column, String, DateTime
from datetime import datetime
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    username = Column(String(50), primary_key=True, index=True)
    password_sha1 = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)