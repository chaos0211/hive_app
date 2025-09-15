from datetime import date, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, func, text, asc, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_session
from app.db.models.rating import AppRatings


router = APIRouter(prefix="/api/v1/predict", tags=["predict"])

# ----------------------------
# Pydantic Schemas
# ----------------------------

class AppLite(BaseModel):
    app_id: str
    app_name: str
    publisher: Optional[str] = None
    icon_url: Optional[str] = None

class TopNItem(BaseModel):
    rank: int = Field(..., description="排名（越小越靠前）")
    app_id: str
    app_name: str
    publisher: Optional[str] = None
    icon_url: Optional[str] = None
    change: Optional[int] = Field(default=None, description="排名变化（正=上升）")
    change_percent: Optional[float] = None

class TopNResponse(BaseModel):
    date: date
    brand: str
    country: str
    device: str
    items: List[TopNItem]

class CategoryOptions(BaseModel):
    items: List[str]

class CountryOptions(BaseModel):
    items: List[str]

class DeviceOptions(BaseModel):
    items: List[str]

class RankPoint(BaseModel):
    d: date
    index: Optional[int] = None

class RankHistoryResponse(BaseModel):
    app_id: str
    country: str
    device: str
    brand: Optional[str] = None
    points: List[RankPoint]


# ----------------------------
# Helpers
# ----------------------------

async def _latest_date(
    session: AsyncSession,
    *,
    country: str,
    device: str,
    brand: Optional[str] = None
) -> Optional[date]:
    """
    获取给定过滤条件下的最新 update_time（榜单日期）。
    """
    stmt = select(func.max(AppRatings.update_time))
    if country:
        stmt = stmt.where(AppRatings.country == country)
    if device:
        stmt = stmt.where(AppRatings.device == device)
    if brand:
        # 若模型中不存在 brand 字段，请将此 where 条件删除
        stmt = stmt.where(AppRatings.brand == brand)

    res = await session.execute(stmt)
    latest: Optional[date] = res.scalar_one_or_none()
    return latest


# ----------------------------
# Option Endpoints
# ----------------------------

@router.get("/options/categories", response_model=CategoryOptions, summary="获取分类（来自 rank_c.genre 的去重）")
async def get_categories(
    country: Optional[str] = Query(None, description="国家代码，如 cn/us"),
    device: Optional[str] = Query(None, description="设备，如 iphone/ipad/android"),
    session: AsyncSession = Depends(get_session),
):
    """
    从 app_ratings.rank_c JSON 中抽取 $.genre 字段去重。
    """
    # MySQL JSON_EXTRACT + JSON_UNQUOTE
    genre_expr = func.json_unquote(func.json_extract(AppRatings.rank_c, '$.genre'))
    stmt = select(func.distinct(genre_expr)).where(genre_expr.is_not(None))

    if country:
        stmt = stmt.where(AppRatings.country == country)
    if device:
        stmt = stmt.where(AppRatings.device == device)

    stmt = stmt.order_by(genre_expr.asc())

    rows = (await session.execute(stmt)).scalars().all()
    # 过滤空字符串与 None
    items = [g for g in rows if g]
    return CategoryOptions(items=items)


@router.get("/options/countries", response_model=CountryOptions, summary="获取国家列表（去重）")
async def get_countries(
    session: AsyncSession = Depends(get_session),
):
    stmt = select(func.distinct(AppRatings.country)).order_by(asc(AppRatings.country))
    rows = (await session.execute(stmt)).scalars().all()
    items = [c for c in rows if c]
    return CountryOptions(items=items)


@router.get("/options/devices", response_model=DeviceOptions, summary="获取设备列表（去重）")
async def get_devices(
    session: AsyncSession = Depends(get_session),
):
    stmt = select(func.distinct(AppRatings.device)).order_by(asc(AppRatings.device))
    rows = (await session.execute(stmt)).scalars().all()
    items = [d for d in rows if d]
    return DeviceOptions(items=items)


# ----------------------------
# Search & Detail
# ----------------------------

@router.get("/apps/search", response_model=List[AppLite], summary="搜索应用（支持 app_id 精确匹配与 app_name 模糊匹配）")
async def search_apps(
    q: str = Query(..., description="关键字；app_id 完全匹配或 app_name 模糊匹配"),
    country: Optional[str] = Query(None),
    device: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    session: AsyncSession = Depends(get_session),
):
    q = (q or "").strip()
    if not q:
        return []

    # app_id 精确；或 app_name 模糊
    stmt = (
        select(
            AppRatings.app_id,
            AppRatings.app_name,
            AppRatings.publisher,
            AppRatings.icon_url,
        )
        .distinct(AppRatings.app_id)
        .limit(limit)
    )

    if country:
        stmt = stmt.where(AppRatings.country == country)
    if device:
        stmt = stmt.where(AppRatings.device == device)

    # WHERE (app_id = :q) OR (app_name LIKE %q%)
    stmt = stmt.where(
        (AppRatings.app_id == q) | (AppRatings.app_name.like(f"%{q}%"))
    )

    rows = await session.execute(stmt)
    items = []
    for app_id, app_name, publisher, icon_url in rows.all():
        items.append(AppLite(app_id=str(app_id), app_name=app_name, publisher=publisher, icon_url=icon_url))
    return items


@router.get("/apps/{app_id}/history", response_model=RankHistoryResponse, summary="获取应用历史排名（用于基线/可视化）")
async def app_history(
    app_id: str,
    days: int = Query(30, ge=1, le=365),
    brand: Optional[str] = Query(None, description="free/paid/grossing，可选"),
    country: str = Query(...),
    device: str = Query(...),
    session: AsyncSession = Depends(get_session),
):
    end_date = await _latest_date(session, country=country, device=device, brand=brand)
    if not end_date:
        return RankHistoryResponse(app_id=app_id, country=country, device=device, brand=brand, points=[])

    start_date = end_date - timedelta(days=days - 1)

    # 以 update_time 为时间维度
    stmt = (
        select(AppRatings.update_time, AppRatings.index)
        .where(AppRatings.app_id == app_id)
        .where(AppRatings.country == country)
        .where(AppRatings.device == device)
        .where(AppRatings.update_time >= start_date)
        .where(AppRatings.update_time <= end_date)
        .order_by(asc(AppRatings.update_time))
    )
    if brand:
        # 若没有 brand 字段请移除此过滤条件
        stmt = stmt.where(AppRatings.brand == brand)

    rows = await session.execute(stmt)
    pts = [RankPoint(d=r[0], index=r[1]) for r in rows.all()]
    return RankHistoryResponse(app_id=app_id, country=country, device=device, brand=brand, points=pts)


# ----------------------------
# TopN （以最新日期为基准）
# ----------------------------

@router.get("/topn", response_model=TopNResponse, summary="获取最新一天 TopN（作为预测TopN的占位/基线数据）")
async def topn_latest(
    brand: Optional[str] = Query(None, description="free/paid/grossing，可选；若模型未存该字段，请忽略"),
    country: str = Query(...),
    device: str = Query(...),
    n: int = Query(10, ge=1, le=50),
    session: AsyncSession = Depends(get_session),
):
    latest = await _latest_date(session, country=country, device=device, brand=brand)
    if not latest:
        return TopNResponse(date=date.today(), brand=brand or "", country=country, device=device, items=[])

    stmt = (
        select(
            AppRatings.index,
            AppRatings.app_id,
            AppRatings.app_name,
            AppRatings.publisher,
            AppRatings.icon_url,
            AppRatings.rank_a,  # 变化值可从 rank_a/b/c 中提取（若存在）
        )
        .where(AppRatings.country == country)
        .where(AppRatings.device == device)
        .where(AppRatings.update_time == latest)
        .order_by(asc(AppRatings.index))
        .limit(n)
    )
    if brand:
        stmt = stmt.where(AppRatings.brand == brand)

    rows = await session.execute(stmt)
    items: List[TopNItem] = []
    for idx, app_id, app_name, publisher, icon_url, rank_a in rows.all():
        change_val = None
        try:
            # rank_a 是 JSON，结构可能为 {"ranking": 12, "change": -3, "genre": "总榜"}
            if rank_a and isinstance(rank_a, dict):
                change_val = rank_a.get("change")
        except Exception:
            change_val = None

        items.append(
            TopNItem(
                rank=int(idx) if idx is not None else 999999,
                app_id=str(app_id),
                app_name=app_name,
                publisher=publisher,
                icon_url=icon_url,
                change=change_val,
                change_percent=None,
            )
        )

    return TopNResponse(date=latest, brand=brand or "", country=country, device=device, items=items)
