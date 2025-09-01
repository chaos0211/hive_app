from sqlalchemy import Column, Integer, BigInteger, String, Date, DateTime, DECIMAL, Boolean, JSON, UniqueConstraint
from sqlalchemy.sql import func
from app.db.base import Base


class AppStoreRankingDaily(Base):
    __tablename__ = "appstore_rankings_daily"

    __table_args__ = (
        UniqueConstraint('chart_date', 'brand_id', 'genre', 'index', 'country', 'device', name='uq_daily_idx'),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # 维度
    chart_date = Column(Date, nullable=False, comment="榜单日期(YYYY-MM-DD)")
    brand_id = Column(Integer, nullable=False, comment="榜单类型: 0付费 / 1免费 / 2畅销")
    country = Column(String(8), nullable=False, default="cn")
    device = Column(String(16), nullable=False, default="iphone")
    genre = Column(String(64), nullable=True)
    app_genre = Column(String(64), nullable=True)

    # 排名
    index = Column(Integer, nullable=True)
    ranking = Column(Integer, nullable=True)
    change = Column(String(16), nullable=True)
    is_ad = Column(Boolean, default=False)

    # 应用信息
    app_id = Column(String(64), nullable=False, index=True)
    app_name = Column(String(255), nullable=False)
    subtitle = Column(String(255), nullable=True)
    icon_url = Column(String(512), nullable=True)
    publisher = Column(String(255), nullable=True)
    publisher_id = Column(String(64), nullable=True)
    price = Column(DECIMAL(10, 2), nullable=True)

    # 体积
    file_size_bytes = Column(BigInteger, nullable=True)
    file_size_mb = Column(DECIMAL(18, 2), nullable=True)
    continuous_first_days = Column(Integer, nullable=True)

    # 其它
    source = Column(String(32), nullable=False, default="qimai")
    raw_json = Column(JSON, nullable=True)

    # 时间
    crawled_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())