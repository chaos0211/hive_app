# app/api/v1/meta.py
from __future__ import annotations

from typing import Any, Dict, List, Optional, Set
import random
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_session  # 你现有的依赖
from app.db.models.ranking import AppStoreRankingDaily  # 你的 ORM 模型

router = APIRouter(prefix="/api/v1", tags=["meta"])

VALID_FIELDS: Set[str] = {"country", "device", "brand_id", "is_ad", "chart_date"}

@router.get("/meta/options")
async def get_meta_options(
    fields: Optional[str] = Query(None, description="用逗号分隔的字段名: country,device,brand_id,is_ad,chart_date"),
    session: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    """
    返回可选项列表（下拉数据）
    - /api/v1/meta/options?fields=country,device,brand_id,is_ad,chart_date
    - 不传 fields 则以上字段都返回
    字段说明：
      * country: 去重后的国家代码列表
      * device: 去重后的设备列表
      * brand_id: 去重后的榜单类型（0=付费,1=免费,2=畅销）
      * is_ad: 固定返回 [0, 1]（即使库中只有单侧值，前端仍可优先展示“全部”）
      * chart_date: 返回 {"min": YYYY-MM-DD, "max": YYYY-MM-DD} 的日期范围
    """
    wanted = set(f.strip().lower() for f in (fields.split(",") if fields else [])) & VALID_FIELDS
    if not wanted:
        wanted = VALID_FIELDS.copy()

    result: Dict[str, Any] = {}

    if "country" in wanted:
        stmt = (
            select(func.distinct(AppStoreRankingDaily.country))
            .where(AppStoreRankingDaily.country.isnot(None))
            .order_by(AppStoreRankingDaily.country.asc())
        )
        rows = (await session.execute(stmt)).scalars().all()
        result["country"] = [r for r in rows if r != ""]

    if "device" in wanted:
        stmt = (
            select(func.distinct(AppStoreRankingDaily.device))
            .where(AppStoreRankingDaily.device.isnot(None))
            .order_by(AppStoreRankingDaily.device.asc())
        )
        rows = (await session.execute(stmt)).scalars().all()
        result["device"] = [r for r in rows if r != ""]

    if "brand_id" in wanted:
        stmt = (
            select(func.distinct(AppStoreRankingDaily.brand_id))
            .where(AppStoreRankingDaily.brand_id.isnot(None))
            .order_by(AppStoreRankingDaily.brand_id.asc())
        )
        rows = (await session.execute(stmt)).scalars().all()
        # 只保留非空整数
        result["brand_id"] = [int(r) for r in rows if r is not None]

    if "is_ad" in wanted:
        result["is_ad"] = [0, 1]

    if "chart_date" in wanted:
        stmt = select(func.min(AppStoreRankingDaily.chart_date), func.max(AppStoreRankingDaily.chart_date))
        minmax = (await session.execute(stmt)).first() or (None, None)
        min_d, max_d = minmax
        result["chart_date"] = {
            "min": str(min_d) if min_d is not None else None,
            "max": str(max_d) if max_d is not None else None,
        }

    return result


# --- New Endpoints ---

@router.get("/meta/overview/collection")
async def get_overview_collection(
    session: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    """
    昨日采集量（以榜单日期 chart_date 为口径）：
    - 取最近两个 chart_date（去重，倒序）
    - 返回最近 chart_date 的总行数作为采集量
    - delta_percent 按需求仍为随机模拟值（-5% ~ +5%）
    """
    # 最近两个榜单日期
    stmt_dates = (
        select(AppStoreRankingDaily.chart_date)
        .distinct()
        .order_by(AppStoreRankingDaily.chart_date.desc())
        .limit(2)
    )
    dates = (await session.execute(stmt_dates)).scalars().all()
    if not dates:
        return {"date": None, "count": 0, "delta_percent": 0.0}

    latest_chart_date = dates[0]
    prev_chart_date = dates[1] if len(dates) > 1 else None

    # 统计最近 chart_date 的行数
    stmt_count_latest = select(func.count()).where(AppStoreRankingDaily.chart_date == latest_chart_date)
    latest_count = (await session.execute(stmt_count_latest)).scalar() or 0

    # （可选）如需真实环比，可同时统计 prev_chart_date 再计算百分比；
    # 目前按需求使用随机百分比，保持前端展示的“涨跌箭头”联动。
    delta_percent = round(random.uniform(-5, 5), 1)

    return {
        "date": str(latest_chart_date),
        "count": latest_count,
        "delta_percent": delta_percent,
    }


@router.get("/meta/overview/top1")
async def get_overview_top1(
    session: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    """
    返回最新榜单日期的第一名应用信息。
    """
    # 获取最新 chart_date
    stmt_date = (
        select(AppStoreRankingDaily.chart_date)
        .order_by(AppStoreRankingDaily.chart_date.desc())
        .limit(1)
    )
    latest_chart_date = (await session.execute(stmt_date)).scalar()
    if not latest_chart_date:
        return {"chart_date": None, "app_name": None, "app_genre": None, "publisher": None}
    # 查询 index=1 的应用
    stmt_top1 = (
        select(
            AppStoreRankingDaily.chart_date,
            AppStoreRankingDaily.app_name,
            AppStoreRankingDaily.app_genre,
            AppStoreRankingDaily.publisher,
        )
        .where(
            AppStoreRankingDaily.chart_date == latest_chart_date,
            AppStoreRankingDaily.index == 1,
        )
        .limit(1)
    )
    row = (await session.execute(stmt_top1)).first()
    if not row:
        return {"chart_date": str(latest_chart_date), "app_name": None, "app_genre": None, "publisher": None}
    return {
        "chart_date": str(row.chart_date),
        "app_name": row.app_name,
        "app_genre": row.app_genre,
        "publisher": row.publisher,
    }


@router.get("/meta/overview/top_category")
async def get_overview_top_category(
    session: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    """
    返回最新榜单日期出现最多的分类（app_genre）及其占比。
    """
    # 获取最新 chart_date
    stmt_date = (
        select(AppStoreRankingDaily.chart_date)
        .order_by(AppStoreRankingDaily.chart_date.desc())
        .limit(1)
    )
    latest_chart_date = (await session.execute(stmt_date)).scalar()
    if not latest_chart_date:
        return {"chart_date": None, "app_genre": None, "count": 0, "ratio": 0.0}
    # 分组统计 app_genre 数量
    stmt_group = (
        select(AppStoreRankingDaily.app_genre, func.count().label("cnt"))
        .where(AppStoreRankingDaily.chart_date == latest_chart_date)
        .group_by(AppStoreRankingDaily.app_genre)
    )
    rows = (await session.execute(stmt_group)).all()
    if not rows:
        return {"chart_date": str(latest_chart_date), "app_genre": None, "count": 0, "ratio": 0.0}
    # 找到最大类别
    top_row = max(rows, key=lambda r: r.cnt)
    total = sum(r.cnt for r in rows)
    ratio = round(top_row.cnt / total * 100, 1) if total > 0 else 0.0
    return {
        "chart_date": str(latest_chart_date),
        "app_genre": top_row.app_genre,
        "count": top_row.cnt,
        "ratio": ratio,
    }