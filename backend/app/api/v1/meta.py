# app/api/v1/meta.py
from __future__ import annotations

from typing import Any, Dict, List, Optional, Set
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