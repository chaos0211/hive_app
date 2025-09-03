# app/db/models/rating.py
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Date, Integer, DECIMAL
from app.db.base import Base

class AppRatingsDaily(Base):
    __tablename__ = "app_ratings_daily"
    app_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    country: Mapped[str] = mapped_column(String(8), primary_key=True)
    device: Mapped[str] = mapped_column(String(16), primary_key=True)
    chart_date: Mapped[Date] = mapped_column(Date, primary_key=True)
    app_name: Mapped[str] = mapped_column(String(255))
    rating: Mapped[float] = mapped_column(DECIMAL(2,1))
    rating_count: Mapped[int] = mapped_column(Integer)
    star_1_count: Mapped[int] = mapped_column(Integer)
    star_2_count: Mapped[int] = mapped_column(Integer)
    star_3_count: Mapped[int] = mapped_column(Integer)
    star_4_count: Mapped[int] = mapped_column(Integer)
    star_5_count: Mapped[int] = mapped_column(Integer)