# app/db/models/monetization.py
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Date, Integer, DECIMAL
from app.db.base import Base

class AppMonetizationDaily(Base):
    __tablename__ = "app_monetization_daily"
    app_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    country: Mapped[str] = mapped_column(String(8), primary_key=True)
    device: Mapped[str] = mapped_column(String(16), primary_key=True)
    chart_date: Mapped[Date] = mapped_column(Date, primary_key=True)
    app_name: Mapped[str] = mapped_column(String(255))
    downloads: Mapped[int] = mapped_column(Integer)
    revenue: Mapped[float] = mapped_column(DECIMAL(18,2))