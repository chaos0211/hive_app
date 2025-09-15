# app/db/models/rating.py
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Date, Integer, DECIMAL, UniqueConstraint
from app.db.base import Base

# class AppRatingsDaily(Base):
#     __tablename__ = "app_ratings_daily"
#     app_id: Mapped[str] = mapped_column(String(64), primary_key=True)
#     country: Mapped[str] = mapped_column(String(8), primary_key=True)
#     device: Mapped[str] = mapped_column(String(16), primary_key=True)
#     chart_date: Mapped[Date] = mapped_column(Date, primary_key=True)
#     app_name: Mapped[str] = mapped_column(String(255))
#     rating: Mapped[float] = mapped_column(DECIMAL(2,1))
#     rating_count: Mapped[int] = mapped_column(Integer)
#     star_1_count: Mapped[int] = mapped_column(Integer)
#     star_2_count: Mapped[int] = mapped_column(Integer)
#     star_3_count: Mapped[int] = mapped_column(Integer)
#     star_4_count: Mapped[int] = mapped_column(Integer)
#     star_5_count: Mapped[int] = mapped_column(Integer)


# 新增模型: AppRatings
class AppRatings(Base):
    """
    存储从七麦 rank/index 接口获取的应用评分及关键词等扩展数据
    """
    __tablename__ = "app_ratings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    app_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True, comment="应用ID")
    app_name: Mapped[str] = mapped_column(String(255), nullable=True, comment="应用名称")
    publisher: Mapped[str] = mapped_column(String(255), nullable=True, comment="发行者")
    country: Mapped[str] = mapped_column(String(8), nullable=False, comment="国家，如cn、us")
    device: Mapped[str] = mapped_column(String(16), nullable=False, comment="设备，如iphone")
    chart_date: Mapped[Date] = mapped_column(Date, nullable=False, comment="榜单日期")
    last_release_time: Mapped[Date] = mapped_column(Date, nullable=True, comment="最后发布时间，如2025-09-12")
    update_time: Mapped[Date] = mapped_column(Date, nullable=False, comment="数据更新时间(爬取时间)，如2025-09-12")
    index: Mapped[int] = mapped_column(Integer, nullable=True, comment="排行榜 index")
    genre: Mapped[str] = mapped_column(String(64), nullable=True, comment="分类，如娱乐、工具")
    keyword_cover: Mapped[int] = mapped_column(Integer, nullable=True, comment="关键词指数")
    keyword_cover_top3: Mapped[int] = mapped_column(Integer, nullable=True, comment="Top3关键词覆盖指数")
    rank_a: Mapped[str] = mapped_column(String(255), nullable=True, comment="总榜排名 JSON")
    rank_b: Mapped[str] = mapped_column(String(255), nullable=True, comment="应用榜排名 JSON")
    rank_c: Mapped[str] = mapped_column(String(255), nullable=True, comment="子分类排名 JSON")
    rating: Mapped[float] = mapped_column(DECIMAL(2,1), nullable=True, comment="评分")
    rating_num: Mapped[str] = mapped_column(String(64), nullable=True, comment="评分总数，原始字符串如132万")
    is_ad: Mapped[bool] = mapped_column(Integer, nullable=True, comment="是否有广告")
    icon_url: Mapped[str] = mapped_column(String(512), nullable=True, comment="图标 URL")
    raw_json: Mapped[str] = mapped_column(String(2000), nullable=True, comment="原始 JSON 数据")

    __table_args__ = (
        UniqueConstraint('chart_date', 'country', 'device', 'app_id', name='uq_ratings_dim'),
    )