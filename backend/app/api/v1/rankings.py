# api/rankings.py
from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Dict, List, Optional, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from sqlalchemy import and_, asc, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_session
from app.db.models.rating import AppRatings

router = APIRouter(prefix="/api/v1", tags=["rankings"])

# ---- Configs ----
# Whitelist of sortable columns on the model to avoid SQL injection via sort_by
ALLOWED_SORT_COLUMNS = {
    "id": AppRatings.id,
    "chart_date": AppRatings.chart_date,
    "update_time": AppRatings.update_time,
    "last_release_time": AppRatings.last_release_time,
    "country": AppRatings.country,
    "device": AppRatings.device,
    "genre": AppRatings.genre,
    "index": AppRatings.index,
    "app_id": AppRatings.app_id,
    "app_name": AppRatings.app_name,
    "publisher": AppRatings.publisher,
    "keyword_cover": AppRatings.keyword_cover,
    "keyword_cover_top3": AppRatings.keyword_cover_top3,
    "rating": AppRatings.rating,
    "rating_num": AppRatings.rating_num,
    "is_ad": AppRatings.is_ad,
}

DEFAULT_SORT_BY = "index"
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
        conds.append(AppRatings.chart_date == chart_date)
    if app_genre:
        conds.append(AppRatings.genre.ilike(f"%{app_genre}%"))
    if is_ad is not None:
        conds.append(AppRatings.is_ad == _to_bool_from_int(is_ad))
    if country:
        conds.append(AppRatings.country == country)
    if device:
        conds.append(AppRatings.device == device)
    if genre:
        conds.append(AppRatings.genre.ilike(f"%{genre}%"))
    if conds:
        stmt = stmt.where(and_(*conds))
    return stmt


@router.get("/rankings")
async def get_rankings(
    # ---- Filters ----
    chart_date: Optional[date] = Query(None, description="榜单日期，YYYY-MM-DD"),
    app_genre: Optional[str] = Query(None, description="应用大类，模糊匹配"),
    is_ad: Optional[int] = Query(None, description="是否广告：0/1"),
    price_min: Optional[float] = Query(None, ge=0),  # 该参数被忽略
    price_max: Optional[float] = Query(None, ge=0),  # 该参数被忽略
    brand_id: Optional[int] = Query(None, description="0=付费,1=免费,2=畅销"),  # 该参数被忽略
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
    注意：自本次调整起，数据来自 AppRatings，`rank_a`/`rank_b`/`rank_c` 为 JSON 字段；`brand_id` 与价格过滤在该接口中被忽略。
    """
    # Base
    base_stmt = select(AppRatings)
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
    sort_key = sort_by if sort_by in ALLOWED_SORT_COLUMNS else DEFAULT_SORT_BY
    sort_col = ALLOWED_SORT_COLUMNS[sort_key]
    order_clause = asc(sort_col) if sort_dir == "asc" else desc(sort_col)

    # Page slice
    page_stmt = base_stmt.order_by(order_clause).offset((page - 1) * page_size).limit(page_size)

    # Execute
    result = await session.execute(page_stmt)
    rows = result.scalars().all()
    items: List[Dict[str, Any]] = [_row_to_dict(r) for r in rows]

    payload = {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }
    return jsonable_encoder(payload)

def _parse_app_ids(v: Optional[str], repeats: List[str]) -> List[str]:
    # 支持逗号分隔和重复参数
    collected = []
    if v:
        collected += [x.strip() for x in v.split(",") if x.strip()]
    for r in repeats:
        collected += [x.strip() for x in r.split(",") if x.strip()]
    # 去重保持顺序
    seen = set()
    out = []
    for a in collected:
        if a not in seen:
            seen.add(a)
            out.append(a)
    return out

@router.get("/rankings/trend")
async def rankings_trend(
    app_ids: Optional[str] = Query(None, description="逗号分隔的 app_id 列表"),
    app_ids_repeat: List[str] = Query([], alias="app_ids"),
    country: str = Query(...),
    device: str = Query(...),
    brand_id: Optional[int] = Query(None, ge=0, le=2),
    window: Optional[int] = Query(7, ge=1, le=365),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    fill_missing: bool = Query(True),
    max_points: int = Query(370),
    session: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    # 解析 app_ids
    ids = _parse_app_ids(app_ids, app_ids_repeat)
    if not ids:
        raise HTTPException(status_code=400, detail="app_ids 不能为空")

    # 校验时间窗口互斥
    if window and (date_from or date_to):
        raise HTTPException(status_code=400, detail="window 与 date_from/date_to 不能同时使用")

    if window:
        date_to = date.today()
        date_from = date_to - timedelta(days=window - 1)
    else:
        # 显式范围必须成对
        if bool(date_from) ^ bool(date_to):
            raise HTTPException(status_code=400, detail="date_from 与 date_to 需同时提供")
        if not date_from or not date_to:
            # 兜底：默认近7天
            date_to = date.today()
            date_from = date_to - timedelta(days=6)

    # 限制点数规模
    span_days = (date_to - date_from).days + 1
    if span_days * len(ids) > max_points:
        raise HTTPException(
            status_code=400,
            detail=f"请求点数过多：{span_days}天 × {len(ids)} apps > {max_points}，请缩小范围或减少应用数",
        )

    # —— 查询每个 app 的时间序列 ——
    where_base = [
        AppStoreRankingDaily.country == country,
        AppStoreRankingDaily.device == device,
        AppStoreRankingDaily.app_id.in_(ids),
        AppStoreRankingDaily.chart_date.between(date_from, date_to),
    ]
    # brand 过滤 / 聚合
    if brand_id is None:
        # 不限定 brand：同日取最优名次（min(ranking)）
        stmt = (
            select(
                AppStoreRankingDaily.app_id.label("app_id"),
                AppStoreRankingDaily.chart_date.label("chart_date"),
                func.min(AppStoreRankingDaily.ranking).label("ranking"),
            )
            .where(*where_base)
            .group_by(AppStoreRankingDaily.app_id, AppStoreRankingDaily.chart_date)
            .order_by(AppStoreRankingDaily.app_id.asc(), AppStoreRankingDaily.chart_date.asc())
        )
    else:
        stmt = (
            select(
                AppStoreRankingDaily.app_id.label("app_id"),
                AppStoreRankingDaily.chart_date.label("chart_date"),
                AppStoreRankingDaily.ranking.label("ranking"),
            )
            .where(*where_base, AppStoreRankingDaily.brand_id == brand_id)
            .order_by(AppStoreRankingDaily.app_id.asc(), AppStoreRankingDaily.chart_date.asc())
        )

    res = await session.execute(stmt)
    rows = res.all()  # [(app_id, chart_date, ranking), ...]

    # 构建 {app_id: {date: ranking}}
    series_map: Dict[str, Dict[date, Optional[int]]] = {a: {} for a in ids}
    for app_id, d, r in rows:
        # r 可能为 None
        series_map.setdefault(app_id, {})[d] = r

    # —— 为卡片取 app 显示信息（范围内最近一条） ——
    meta_map: Dict[str, Dict[str, Optional[str]]] = {a: {} for a in ids}
    for a in ids:
        sub_max = (
            select(func.max(AppStoreRankingDaily.chart_date))
            .where(
                AppStoreRankingDaily.app_id == a,
                AppStoreRankingDaily.country == country,
                AppStoreRankingDaily.device == device,
                AppStoreRankingDaily.chart_date.between(date_from, date_to),
            )
            .scalar_subquery()
        )
        meta_stmt = (
            select(
                AppStoreRankingDaily.app_name,
                AppStoreRankingDaily.icon_url,
                AppStoreRankingDaily.publisher,
            )
            .where(
                AppStoreRankingDaily.app_id == a,
                AppStoreRankingDaily.country == country,
                AppStoreRankingDaily.device == device,
                AppStoreRankingDaily.chart_date == sub_max,
            )
            .limit(1)
        )
        meta_res = await session.execute(meta_stmt)
        row = meta_res.first()
        if row:
            meta_map[a] = {
                "app_name": row[0],
                "icon_url": row[1],
                "publisher": row[2],
            }
        else:
            # 范围内无记录：留空
            meta_map[a] = {"app_name": None, "icon_url": None, "publisher": None}

    # —— 生成完整 points ——
    all_dates = [date_from + timedelta(days=i) for i in range(span_days)]
    series: List[Dict[str, Any]] = []
    for a in ids:
        name = meta_map[a].get("app_name")
        icon = meta_map[a].get("icon_url")
        pub  = meta_map[a].get("publisher")
        day_map = series_map.get(a, {})

        if fill_missing:
            pts = [[d.isoformat(), day_map.get(d, None)] for d in all_dates]
        else:
            pts = [[d.isoformat(), day_map[d]] for d in sorted(day_map.keys())]

        series.append({
            "app_id": a,
            "app_name": name,
            "icon_url": icon,
            "publisher": pub,
            "points": pts,
        })

    payload = {
        "meta": {
            "country": country,
            "device": device,
            "brand_id": brand_id,
            "date_from": date_from.isoformat(),
            "date_to": date_to.isoformat(),
            "window": window or span_days,
            "fill_missing": fill_missing,
        },
        "series": series,
    }
    return jsonable_encoder(payload)


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