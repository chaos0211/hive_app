# api/rankings.py
from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, asc, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_session
from app.db.models.ranking import AppStoreRankingDaily

router = APIRouter(prefix="/api/v1", tags=["rankings"])

# ---- Configs ----
# Whitelist of sortable columns on the model to avoid SQL injection via sort_by
ALLOWED_SORT_COLUMNS = {
    "id": AppStoreRankingDaily.id,
    "chart_date": AppStoreRankingDaily.chart_date,
    "brand_id": AppStoreRankingDaily.brand_id,
    "country": AppStoreRankingDaily.country,
    "device": AppStoreRankingDaily.device,
    "genre": AppStoreRankingDaily.genre,
    "app_genre": AppStoreRankingDaily.app_genre,
    "index": AppStoreRankingDaily.index,
    "ranking": AppStoreRankingDaily.ranking,
    "change": AppStoreRankingDaily.change,
    "is_ad": AppStoreRankingDaily.is_ad,
    "app_id": AppStoreRankingDaily.app_id,
    "app_name": AppStoreRankingDaily.app_name,
    "publisher": AppStoreRankingDaily.publisher,
    "price": AppStoreRankingDaily.price,
    "file_size_mb": AppStoreRankingDaily.file_size_mb,
    "continuous_first_days": AppStoreRankingDaily.continuous_first_days,
    "source": AppStoreRankingDaily.source,
    "crawled_at": AppStoreRankingDaily.crawled_at,
    "updated_at": AppStoreRankingDaily.updated_at,
}

DEFAULT_SORT_BY = "ranking"
DEFAULT_SORT_DIR: Literal["asc", "desc"] = "asc"
MAX_PAGE_SIZE = 200


def _to_bool_from_int(x: Optional[int]) -> Optional[bool]:
    if x is None:
        return None
    if x in (0, 1):
        return bool(x)
    raise HTTPException(status_code=422, detail="is_ad must be 0 or 1")


def _row_to_dict(obj: Any) -> Dict[str, Any]:
    if hasattr(obj, "to_dict"):
        return obj.to_dict()  # type: ignore[attr-defined]
    # Fallback generic serializer
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}  # type: ignore[attr-defined]


def _apply_filters(
    stmt,
    *,
    chart_date: Optional[date],
    app_genre: Optional[str],
    is_ad: Optional[int],
    price_min: Optional[float],
    price_max: Optional[float],
    brand_id: Optional[int],
    country: Optional[str],
    device: Optional[str],
    genre: Optional[str],
):
    conds = []
    if chart_date:
        conds.append(AppStoreRankingDaily.chart_date == chart_date)
    if app_genre:
        conds.append(AppStoreRankingDaily.app_genre.ilike(f"%{app_genre}%"))
    if is_ad is not None:
        conds.append(AppStoreRankingDaily.is_ad == _to_bool_from_int(is_ad))
    if price_min is not None:
        conds.append(AppStoreRankingDaily.price >= price_min)
    if price_max is not None:
        conds.append(AppStoreRankingDaily.price <= price_max)
    if brand_id is not None:
        conds.append(AppStoreRankingDaily.brand_id == brand_id)
    if country:
        conds.append(AppStoreRankingDaily.country == country)
    if device:
        conds.append(AppStoreRankingDaily.device == device)
    if genre:
        conds.append(AppStoreRankingDaily.genre.ilike(f"%{genre}%"))
    if conds:
        stmt = stmt.where(and_(*conds))
    return stmt


@router.get("/rankings")
async def get_rankings(
    # ---- Filters ----
    chart_date: Optional[date] = Query(None, description="榜单日期，YYYY-MM-DD"),
    app_genre: Optional[str] = Query(None, description="应用大类，模糊匹配"),
    is_ad: Optional[int] = Query(None, description="是否广告：0/1"),
    price_min: Optional[float] = Query(None, ge=0),
    price_max: Optional[float] = Query(None, ge=0),
    brand_id: Optional[int] = Query(None, description="0=付费,1=免费,2=畅销"),
    country: Optional[str] = None,
    device: Optional[str] = None,
    genre: Optional[str] = Query(None, description="榜单细分，模糊匹配"),
    # ---- Sorting ----
    sort_by: str = Query(DEFAULT_SORT_BY, description=f"排序字段，允许：{', '.join(ALLOWED_SORT_COLUMNS.keys())}"),
    sort_dir: Literal["asc", "desc"] = Query(DEFAULT_SORT_DIR),
    # ---- Pagination ----
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=MAX_PAGE_SIZE),
    session: AsyncSession = Depends(get_session),
):
    """
    应用榜单 - 列表接口
    - 支持多条件组合筛选
    - 排序字段白名单 + 升/降序
    - 分页返回 {items, total, page, page_size}
    """
    # Base
    base_stmt = select(AppStoreRankingDaily)
    base_stmt = _apply_filters(
        base_stmt,
        chart_date=chart_date,
        app_genre=app_genre,
        is_ad=is_ad,
        price_min=price_min,
        price_max=price_max,
        brand_id=brand_id,
        country=country,
        device=device,
        genre=genre,
    )

    # Total count
    count_stmt = select(func.count()).select_from(base_stmt.order_by(None).subquery())
    total_result = await session.execute(count_stmt)
    total: int = int(total_result.scalar_one() or 0)

    # Sorting (whitelist)
    sort_col = ALLOWED_SORT_COLUMNS.get(sort_by, ALLOWED_SORT_COLUMNS[DEFAULT_SORT_BY])
    order_clause = asc(sort_col) if sort_dir == "asc" else desc(sort_col)

    # Page slice
    page_stmt = base_stmt.order_by(order_clause).offset((page - 1) * page_size).limit(page_size)

    # Execute
    result = await session.execute(page_stmt)
    rows = result.scalars().all()
    items: List[Dict[str, Any]] = [_row_to_dict(r) for r in rows]

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


# --- Optional: direct invocation for quick local test ---
if __name__ == "__main__":
    import asyncio
    import json
    from app.db.base import async_session, engine

    async def _test():
        async with async_session() as session:
            res = await get_rankings(
                chart_date=None,
                app_genre=None,
                is_ad=None,
                price_min=None,
                price_max=None,
                brand_id=None,
                country=None,
                device=None,
                genre=None,
                sort_by="ranking",
                sort_dir="asc",
                page=1,
                page_size=5,
                session=session,
            )
            print(json.dumps(res, ensure_ascii=False, indent=2, default=str))
        # dispose before closing loop to avoid "Event loop is closed" warnings
        await engine.dispose()

    asyncio.run(_test())