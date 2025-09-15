# app/api/v1/apps.py
from __future__ import annotations

from typing import Dict, List, Optional, Any
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, func, and_, literal
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_session
from app.db.models.ranking import AppStoreRankingDaily
from app.db.models.rating import AppRatings

# try:
#     from app.db.models.app import AppInfo  # 可选：应用元数据(如不存在则跳过)
# except Exception:
#     AppInfo = None  # type: ignore

router = APIRouter(prefix="/api/v1", tags=["apps"])

async def _latest_ranking_row(session: AsyncSession, app_id: str, country: Optional[str], device: Optional[str], date_from: Optional[date] = None, date_to: Optional[date] = None):
    where = [AppStoreRankingDaily.app_id == app_id]
    if country:
        where.append(AppStoreRankingDaily.country == country)
    if device:
        where.append(AppStoreRankingDaily.device == device)
    if date_from and date_to:
        where.append(AppStoreRankingDaily.chart_date.between(date_from, date_to))
    sub = (
        select(func.max(AppStoreRankingDaily.chart_date).label("max_d"))
        .where(*where)
        .scalar_subquery()
    )
    stmt = (
        select(AppStoreRankingDaily)
        .where(*where, AppStoreRankingDaily.chart_date == sub)
        .limit(1)
    )
    res = await session.execute(stmt)
    return res.scalars().first()

def _row_to_obj(row) -> Dict[str, Optional[str]]:
    m = getattr(row, "_mapping", None)
    if m is None:
        # ORM instance or tuple fallback
        try:
            app_id = row.app_id
            app_name = getattr(row, "app_name", None)
            icon_url = getattr(row, "icon_url", None)
            publisher = getattr(row, "publisher", None)
        except AttributeError:
            app_id = row[0] if isinstance(row, (list, tuple)) and row else None
            app_name = row[1] if isinstance(row, (list, tuple)) and len(row) > 1 else None
            icon_url = row[2] if isinstance(row, (list, tuple)) and len(row) > 2 else None
            publisher = row[3] if isinstance(row, (list, tuple)) and len(row) > 3 else None
    else:
        app_id = m.get("app_id")
        app_name = m.get("app_name")
        icon_url = m.get("icon_url")
        publisher = m.get("publisher")
    return {
        "app_id": app_id,
        "app_name": app_name,
        "icon_url": icon_url,
        "publisher": publisher,
    }

@router.get("/apps/search")
async def search_apps(
    q: str = Query(..., min_length=1, description="应用名(模糊) 或 app_id(精确)"),
    limit: int = Query(20, ge=1, le=50),  # 默认 20，前端可控；前端可用 5 和 10 的两档
    country: Optional[str] = Query(None, description="区域，如 cn、us"),
    device: Optional[str] = Query(None, description="设备，如 iphone、ipad、android"),
    brand: Optional[str] = Query(None, description="榜单类型：free/paid/grossing，可选"),
    genre: Optional[str] = Query(None, description="榜单分类（使用 rank_c->genre 过滤）"),
    window: Optional[int] = Query(None, ge=1, le=366, description="最近N天，和 date_from/date_to 互斥"),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    session: AsyncSession = Depends(get_session),
) -> Dict[str, List[Dict[str, Optional[str]]]]:
    """
    搜索应用：
    - app_id：去空格后精确匹配
    - app_name：模糊匹配（LIKE %q%）
    在筛选范围内（国家/设备/品牌/时间）返回按最近日期排序的去重 app 列表（按 app_id 去重）。
    若命中不足，再用无筛选的名称模糊补足。
    """
    q_raw = q or ""
    q_trim = q_raw.strip()
    if not q_trim:
        return {"items": []}

    # 解析日期窗口
    if window and (date_from or date_to):
        raise HTTPException(status_code=400, detail="window 与 date_from/date_to 不能同时使用")
    if window:
        date_to = date.today()
        date_from = date_to - timedelta(days=window)

    where_clauses = []
    if country:
        where_clauses.append(AppRatings.country == country)
    if device:
        where_clauses.append(AppRatings.device == device)
    if brand:
        where_clauses.append(AppRatings.brand == brand)
    if genre:
        # 兼容不同数据库方言
        try:
            dialect_name = session.bind.dialect.name  # 'postgresql', 'mysql', 'sqlite', etc.
        except Exception:
            dialect_name = None
        rank_c_col = AppRatings.rank_c
        where_clauses.append(rank_c_col.isnot(None))
        if dialect_name == "postgresql":
            where_clauses.append(rank_c_col["genre"].astext == genre)
        else:
            # MySQL / SQLite(JSON1)
            where_clauses.append(func.json_extract(rank_c_col, "$.genre") == genre)
    if date_from and date_to:
        where_clauses.append(AppRatings.chart_date.between(date_from, date_to))

    # 子查询：在筛选范围内，找到每个 app 的最近日期，用于去重与排序
    base_filtered = select(
        AppRatings.app_id,
        func.max(AppRatings.chart_date).label("max_d")
    ).where(
        *where_clauses
    ).group_by(AppRatings.app_id).subquery()

    items: List[Dict[str, Optional[str]]] = []
    seen = set()

    # 1) app_id 精确命中（带筛选约束：必须在当前筛选范围内存在记录）
    if q_trim:
        exact_q = (
            select(AppRatings.app_id, AppRatings.app_name, AppRatings.icon_url, AppRatings.publisher)
            .join(base_filtered, AppRatings.app_id == base_filtered.c.app_id)
            .where(AppRatings.app_id == q_trim)
            .order_by(base_filtered.c.max_d.desc())
            .limit(5)
        )
        res = await session.execute(exact_q)
        for row in res:
            obj = _row_to_obj(row)
            aid = obj["app_id"]
            if aid and aid not in seen:
                seen.add(aid)
                items.append(obj)
                if len(items) >= limit:
                    return {"items": items}

    # 2) 名称模糊匹配（仍需存在于筛选范围内）
    like_q = (
        select(AppRatings.app_id, AppRatings.app_name, AppRatings.icon_url, AppRatings.publisher)
        .join(base_filtered, AppRatings.app_id == base_filtered.c.app_id)
        .where(AppRatings.app_name.ilike(f"%{q_trim}%"))
        .group_by(AppRatings.app_id, AppRatings.app_name, AppRatings.icon_url, AppRatings.publisher)
        .order_by(base_filtered.c.max_d.desc(), AppRatings.app_name.asc())
        .limit(max(limit * 3, 50))
    )
    res2 = await session.execute(like_q)
    for row in res2:
        obj = _row_to_obj(row)
        aid = obj["app_id"]
        if aid and aid not in seen:
            seen.add(aid)
            items.append(obj)
            if len(items) >= limit:
                break

    # --- Fallback（仅当未指定任何筛选条件时才放宽）---
    if len(items) < limit and not where_clauses:
        unfiltered_like_q = (
            select(AppRatings.app_id, AppRatings.app_name, AppRatings.icon_url, AppRatings.publisher)
            .where(AppRatings.app_name.ilike(f"%{q_trim}%"))
            .group_by(AppRatings.app_id, AppRatings.app_name, AppRatings.icon_url, AppRatings.publisher)
            .order_by(AppRatings.app_name.asc())
            .limit(limit * 3)
        )
        res3 = await session.execute(unfiltered_like_q)
        for row in res3:
            obj = _row_to_obj(row)
            aid = obj["app_id"]
            if aid and aid not in seen:
                seen.add(aid)
                items.append(obj)
                if len(items) >= limit:
                    break

    return {"items": items}

@router.get("/apps/{app_id}")
async def get_app_detail(
    app_id: str,
    country: Optional[str] = Query(None, description="区域筛选，可选"),
    device: Optional[str] = Query(None, description="设备筛选，可选"),
    window: Optional[int] = Query(None, ge=1, le=366),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    session: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    """返回单个应用的详细信息（用于对比卡片）。
    优先从 AppInfo 读取 icon/publisher；不存在则回退到排名表的最近一条记录，仅返回 app_name。
    """
    app_id = (app_id or "").strip()
    if not app_id:
        raise HTTPException(status_code=400, detail="app_id 不能为空")

    # 解析时间范围（window 与 date_from/date_to 互斥）
    if window and (date_from or date_to):
        raise HTTPException(status_code=400, detail="window 与 date_from/date_to 不能同时使用")
    if window:
        date_to = date.today()
        date_from = date_to - timedelta(days=window)

    # 取筛选范围内该 app 的最近一条记录
    last_row = await _latest_ranking_row(session, app_id, country, device, date_from=date_from, date_to=date_to)
    if last_row is None:
        raise HTTPException(status_code=404, detail="未找到应用或该筛选范围内无数据")

    # 序列化：将 SQLAlchemy 对象转为可 JSON 的字典
    def _to_json(o):
        from decimal import Decimal
        if o is None:
            return None
        if isinstance(o, (date,)):
            return o.isoformat()
        try:
            from datetime import datetime
            if isinstance(o, datetime):
                # 保留到秒
                return o.isoformat()
        except Exception:
            pass
        if isinstance(o, Decimal):
            return float(o)
        return o

    data = {
        # 维度
        "chart_date": _to_json(last_row.chart_date),
        "brand_id": last_row.brand_id,
        "country": last_row.country,
        "device": last_row.device,
        "genre": last_row.genre,
        "app_genre": last_row.app_genre,
        # 排名
        "index": last_row.index,
        "ranking": last_row.ranking,
        "change": last_row.change,
        "is_ad": last_row.is_ad,
        # 应用信息
        "app_id": last_row.app_id,
        "app_name": last_row.app_name,
        "subtitle": last_row.subtitle,
        "icon_url": last_row.icon_url,
        "publisher": last_row.publisher,
        "publisher_id": last_row.publisher_id,
        "price": _to_json(last_row.price),
        # 体积
        "file_size_bytes": last_row.file_size_bytes,
        "file_size_mb": _to_json(last_row.file_size_mb),
        "continuous_first_days": last_row.continuous_first_days,
        # 其它
        "source": last_row.source,
        "raw_json": last_row.raw_json,
        # 时间
        "crawled_at": _to_json(last_row.crawled_at),
        "updated_at": _to_json(last_row.updated_at),
    }

    return jsonable_encoder(data)