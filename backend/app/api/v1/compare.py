# app/api/v1/compare.py
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional, Tuple
from sqlalchemy import select, func, desc, and_
from app.db.base import async_session  # 你已切到 async 版本
from app.db.models.ranking import AppStoreRankingDaily
from app.db.models.rating import AppRatingsDaily     # 新建
from app.db.models.monetization import AppMonetizationDaily  # 新建
from datetime import date, timedelta

router = APIRouter(prefix="/api/v1/compare", tags=["compare"])

# 工具：解析日期窗口
def _window_dates(window: Optional[int]) -> Tuple[Optional[date], Optional[date]]:
    if not window: return None, None
    end = date.today()
    start = end - timedelta(days=window)
    return start, end

@router.get("/apps/basic")
async def apps_basic(
    app_ids: List[str] = Query(..., alias="app_ids"),
    country: str = Query(...),
    device: str = Query(...),
    brand_id: Optional[int] = None,
):
    async with async_session() as s:
        # 取每个 app 最近一天的记录
        sub = (
            select(
                AppStoreRankingDaily.app_id,
                func.max(AppStoreRankingDaily.chart_date).label("max_d")
            )
            .where(
                AppStoreRankingDaily.app_id.in_(app_ids),
                AppStoreRankingDaily.country == country,
                AppStoreRankingDaily.device == device,
                *( [AppStoreRankingDaily.brand_id == brand_id] if brand_id is not None else [] )
            )
            .group_by(AppStoreRankingDaily.app_id)
            .subquery()
        )
        q = (
            select(AppStoreRankingDaily)
            .join(sub, and_(
                AppStoreRankingDaily.app_id == sub.c.app_id,
                AppStoreRankingDaily.chart_date == sub.c.max_d
            ))
        )
        rows = (await s.execute(q)).scalars().all()

    # 映射到前端需要的基础信息；缺就 None
    items = []
    for r in rows:
        items.append({
            "app_id": r.app_id,
            "app_name": r.app_name,
            "company": None,
            "price": None,
            "latest_version": None,
            "size_mb": None,
            "age_rating": None,
            "languages": None,
        })
    return {"items": items}

@router.get("/ratings")
async def ratings(
    app_ids: List[str] = Query(...),
    country: str = Query(...),
    device: str = Query(...),
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
):
    async with async_session() as s:
        if not (date_from and date_to):
            # 默认取最新一天
            sub = (
                select(
                    AppRatingsDaily.app_id,
                    func.max(AppRatingsDaily.chart_date).label("max_d")
                )
                .where(
                    AppRatingsDaily.app_id.in_(app_ids),
                    AppRatingsDaily.country == country,
                    AppRatingsDaily.device == device
                )
                .group_by(AppRatingsDaily.app_id)
                .subquery()
            )
            q = (select(AppRatingsDaily)
                 .join(sub, and_(AppRatingsDaily.app_id == sub.c.app_id,
                                 AppRatingsDaily.chart_date == sub.c.max_d)))
            rows = (await s.execute(q)).scalars().all()
        else:
            # 区间聚合（平均分建议加权，示例先简单平均/求和）
            q = (
                select(
                    AppRatingsDaily.app_id,
                    func.max(AppRatingsDaily.app_name),
                    func.round(func.avg(AppRatingsDaily.rating), 1).label("rating"),
                    func.sum(AppRatingsDaily.rating_count).label("rating_count"),
                    func.sum(AppRatingsDaily.star_1_count), func.sum(AppRatingsDaily.star_2_count),
                    func.sum(AppRatingsDaily.star_3_count), func.sum(AppRatingsDaily.star_4_count),
                    func.sum(AppRatingsDaily.star_5_count),
                )
                .where(
                    AppRatingsDaily.app_id.in_(app_ids),
                    AppRatingsDaily.country == country,
                    AppRatingsDaily.device == device,
                    AppRatingsDaily.chart_date.between(date_from, date_to),
                )
                .group_by(AppRatingsDaily.app_id)
            )
            rows = (await s.execute(q)).all()

    items = []
    for r in rows:
        # r 可能是 ORM 或 Row，分别取值
        obj = getattr(r, "_mapping", None)
        if obj:
            app_id = obj[AppRatingsDaily.app_id]
            app_name = obj[1]
            rating = obj["rating"]
            rating_count = obj["rating_count"]
            s1, s2, s3, s4, s5 = obj[4], obj[5], obj[6], obj[7], obj[8]
        else:
            app_id = r.app_id; app_name = r.app_name
            rating = r.rating; rating_count = r.rating_count
            s1, s2, s3, s4, s5 = r.star_1_count, r.star_2_count, r.star_3_count, r.star_4_count, r.star_5_count

        items.append({
            "app_id": app_id, "app_name": app_name,
            "rating": rating, "rating_count": rating_count,
            "stars": {"1": s1, "2": s2, "3": s3, "4": s4, "5": s5}
        })
    return {"items": items}

@router.get("/ranking_trend")
async def ranking_trend(
    app_ids: List[str] = Query(...),
    country: str = Query(...),
    device: str = Query(...),
    brand_id: Optional[int] = None,
    window: Optional[int] = Query(None, ge=1, le=366),
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
):
    if window and (date_from or date_to):
        raise HTTPException(400, "window 与 date_from/date_to 只能选一种传参")

    if window:
        date_from, date_to = _window_dates(window)

    async with async_session() as s:
        q = (
            select(
                AppStoreRankingDaily.app_id,
                AppStoreRankingDaily.app_name,
                AppStoreRankingDaily.chart_date,
                AppStoreRankingDaily.ranking,
            )
            .where(
                AppStoreRankingDaily.app_id.in_(app_ids),
                AppStoreRankingDaily.country == country,
                AppStoreRankingDaily.device == device,
                *( [AppStoreRankingDaily.brand_id == brand_id] if brand_id is not None else [] ),
                *( [AppStoreRankingDaily.chart_date.between(date_from, date_to)] if (date_from and date_to) else [] ),
            )
            .order_by(AppStoreRankingDaily.app_id, AppStoreRankingDaily.chart_date)
        )
        rows = (await s.execute(q)).all()

    series_map = {}
    for app_id, app_name, d, rank in rows:
        series_map.setdefault(app_id, {"app_id": app_id, "name": app_name, "points": []})
        series_map[app_id]["points"].append([d.isoformat(), rank])
    return {"series": list(series_map.values()), "y_inverse": True}

@router.get("/monetization")
async def monetization(
    app_ids: List[str] = Query(...),
    country: str = Query(...),
    device: str = Query(...),
    metric: str = Query("downloads", pattern="^(downloads|revenue)$"),
    window: Optional[int] = Query(30, ge=1, le=366),
):
    date_from, date_to = _window_dates(window)
    col = AppMonetizationDaily.downloads if metric == "downloads" else AppMonetizationDaily.revenue

    async with async_session() as s:
        q = (
            select(
                AppMonetizationDaily.app_id,
                AppMonetizationDaily.app_name,
                AppMonetizationDaily.chart_date,
                col.label("val"),
            )
            .where(
                AppMonetizationDaily.app_id.in_(app_ids),
                AppMonetizationDaily.country == country,
                AppMonetizationDaily.device == device,
                AppMonetizationDaily.chart_date.between(date_from, date_to),
            )
            .order_by(AppMonetizationDaily.app_id, AppMonetizationDaily.chart_date)
        )
        rows = (await s.execute(q)).all()

    series_map = {}
    for app_id, app_name, d, v in rows:
        series_map.setdefault(app_id, {"app_id": app_id, "name": app_name, "points": []})
        series_map[app_id]["points"].append([d.isoformat(), float(v) if v is not None else None])

    return {"metric": metric, "series": list(series_map.values())}