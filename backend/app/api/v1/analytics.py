from fastapi import APIRouter, Depends
from typing import Dict, List
from datetime import timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_session
from app.db.models.ranking import AppStoreRankingDaily

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])

@router.get("/kpis")
def kpis():
    return {
        "collect_yesterday": 12845,
        "partitions": 248,
        "top_app": {"name":"手机应用市场","rating":4.8,"category":"工具"},
        "top_category": {"name":"游戏","share":"32.5%","apps":128},
        "predict_cover": 89.7,
        "task_success": 96.2
    }



@router.get("/topn-trend")
async def topn_trend(
    days: int = 7,
    top: int = 5,
    brand_id: int = 1,          # 0=付费, 1=免费, 2=畅销
    country: str = "cn",
    device: str = "iphone",
    session: AsyncSession = Depends(get_session),
):
    """返回最近一次 *chart_date* 的 TOPN 应用在最近 *days* 天的排名趋势。
    - 先确定最近一次有数据的 chart_date（按 brand_id/country/device 过滤）。
    - 在该日期选出排名前 *top* 的 app（以 ranking 升序；MySQL 无 nulls last，则以 NULL 排最后的等价实现）。
    - 回溯最近 days 天，返回这些 app 在各天的排名（缺失用 None）。
    """
    days = max(1, min(days, 366))
    top = max(1, min(top, 50))

    # 1) 最近一次 chart_date
    latest_stmt = (
        select(func.max(AppStoreRankingDaily.chart_date))
        .where(
            AppStoreRankingDaily.brand_id == brand_id,
            AppStoreRankingDaily.country == country,
            AppStoreRankingDaily.device == device,
        )
    )
    latest_date = (await session.execute(latest_stmt)).scalar_one_or_none()
    if not latest_date:
        return {"latest_date": None, "x": [], "series": {}}

    # 2) 该日 TOPN 应用（用“NULL 在后”的排序等价：先按 ranking IS NULL，再按 ranking，再按 index IS NULL，再按 index）
    top_stmt = (
        select(
            AppStoreRankingDaily.app_id,
            AppStoreRankingDaily.app_name,
            AppStoreRankingDaily.ranking,
            AppStoreRankingDaily.index,
        )
        .where(
            AppStoreRankingDaily.chart_date == latest_date,
            AppStoreRankingDaily.brand_id == brand_id,
            AppStoreRankingDaily.country == country,
            AppStoreRankingDaily.device == device,
        )
        .order_by(
            (AppStoreRankingDaily.ranking.is_(None)).asc(),
            AppStoreRankingDaily.ranking.asc(),
            (AppStoreRankingDaily.index.is_(None)).asc(),
            AppStoreRankingDaily.index.asc(),
        )
        .limit(top)
    )
    top_rows = (await session.execute(top_stmt)).all()
    if not top_rows:
        return {"latest_date": str(latest_date), "x": [], "series": {}}

    top_ids = [r[0] for r in top_rows]
    id_to_name = {r[0]: r[1] for r in top_rows}

    # 3) 日期轴（最近 days 天，包含 latest_date）
    start_date = latest_date - timedelta(days=days - 1)
    x_dates = [start_date + timedelta(days=i) for i in range(days)]
    x_labels = [d.isoformat() for d in x_dates]

    # 4) 拉取窗口内排名
    win_stmt = (
        select(
            AppStoreRankingDaily.chart_date,
            AppStoreRankingDaily.app_id,
            AppStoreRankingDaily.ranking,
            AppStoreRankingDaily.index,
        )
        .where(
            AppStoreRankingDaily.chart_date >= start_date,
            AppStoreRankingDaily.chart_date <= latest_date,
            AppStoreRankingDaily.brand_id == brand_id,
            AppStoreRankingDaily.country == country,
            AppStoreRankingDaily.device == device,
            AppStoreRankingDaily.app_id.in_(top_ids),
        )
    )
    all_rows = (await session.execute(win_stmt)).all()

    # 5) 组装 series：app -> [rank or None]
    from typing import Dict, List
    grid: Dict[str, Dict[str, int]] = {}
    for chart_date, app_id, ranking, index in all_rows:
        day = chart_date.isoformat()
        rank_val = ranking if ranking is not None else index
        grid.setdefault(app_id, {})[day] = int(rank_val) if rank_val is not None else None

    series: Dict[str, List[int]] = {}
    for app_id in top_ids:
        name = id_to_name.get(app_id, app_id)
        seq: List[int] = [grid.get(app_id, {}).get(lab, None) for lab in x_labels]
        series[name] = seq

    return {
        "latest_date": latest_date.isoformat(),
        "filters": {"brand_id": brand_id, "country": country, "device": device},
        "x": x_labels,
        "series": series,
    }

@router.get("/top-apps")
async def top_apps(
    brand_id: int = 1,          # 0=付费, 1=免费, 2=畅销
    country: str = "cn",
    device: str = "iphone",
    limit: int = 10,
    session: AsyncSession = Depends(get_session),
):
    """返回最近一次 *chart_date* 的 TopN 应用列表。
    字段包含：app_id, app_name, publisher, app_genre, ranking, chart_date。
    另外计算该日各 app_genre 的占比（genre_share），便于前端显示进度条。
    """
    limit = max(1, min(limit, 50))

    # 1) 最近一次 chart_date
    latest_stmt = (
        select(func.max(AppStoreRankingDaily.chart_date))
        .where(
            AppStoreRankingDaily.brand_id == brand_id,
            AppStoreRankingDaily.country == country,
            AppStoreRankingDaily.device == device,
        )
    )
    latest_date = (await session.execute(latest_stmt)).scalar_one_or_none()
    if not latest_date:
        return []

    # 2) 该日 TopN 应用（ranking 优先，其次 index）
    top_stmt = (
        select(
            AppStoreRankingDaily.app_id,
            AppStoreRankingDaily.app_name,
            AppStoreRankingDaily.publisher,
            AppStoreRankingDaily.app_genre,
            AppStoreRankingDaily.ranking,
            AppStoreRankingDaily.index,
            AppStoreRankingDaily.chart_date,
        )
        .where(
            AppStoreRankingDaily.chart_date == latest_date,
            AppStoreRankingDaily.brand_id == brand_id,
            AppStoreRankingDaily.country == country,
            AppStoreRankingDaily.device == device,
        )
        .order_by(
            (AppStoreRankingDaily.ranking.is_(None)).asc(),
            AppStoreRankingDaily.ranking.asc(),
            (AppStoreRankingDaily.index.is_(None)).asc(),
            AppStoreRankingDaily.index.asc(),
        )
        .limit(limit)
    )
    rows = (await session.execute(top_stmt)).all()

    # 3) 同日、同维度下的 genre 占比（全集）
    genre_stmt = (
        select(AppStoreRankingDaily.app_genre, func.count().label("cnt"))
        .where(
            AppStoreRankingDaily.chart_date == latest_date,
            AppStoreRankingDaily.brand_id == brand_id,
            AppStoreRankingDaily.country == country,
            AppStoreRankingDaily.device == device,
        )
        .group_by(AppStoreRankingDaily.app_genre)
    )
    genre_rows = (await session.execute(genre_stmt)).all()
    genre_counts = { (g or "未知"): int(c) for (g, c) in genre_rows }
    total_count = sum(genre_counts.values()) or 1

    # 4) 组装返回
    result = []
    for app_id, app_name, publisher, app_genre, ranking, index, chart_date in rows:
        rank_val = ranking if ranking is not None else index
        genre_key = app_genre or "未知"
        share = round(genre_counts.get(genre_key, 0) * 100.0 / total_count)
        result.append({
            "app_id": app_id,
            "app_name": app_name,
            "publisher": publisher,
            "app_genre": app_genre,
            "ranking": int(rank_val) if rank_val is not None else None,
            "chart_date": chart_date.isoformat(),
            "genre_share": share,
        })

    return result

@router.get("/category-share")
def category_share():
    return [
        {"name":"游戏","value":325},{"name":"社交","value":244},{"name":"工具","value":188},
        {"name":"娱乐","value":155},{"name":"教育","value":102},{"name":"其他","value":85}
    ]

@router.get("/region-heatmap")
def region_heatmap():
    return [
        {"name":"北京","value":150},{"name":"天津","value":80},{"name":"上海","value":180},
        {"name":"广东","value":170},{"name":"浙江","value":130},{"name":"江苏","value":120},
        {"name":"四川","value":100},{"name":"福建","value":95},{"name":"山东","value":90}
    ]

@router.get("/task-gantt")
def task_gantt():
    return [
        {"name":"数据采集","start":"2023-06-15 08:00","end":"2023-06-15 09:30","color":"#00B42A"},
        {"name":"数据清洗","start":"2023-06-15 09:30","end":"2023-06-15 10:45","color":"#00B42A"},
        {"name":"数据分析","start":"2023-06-15 10:45","end":"2023-06-15 12:30","color":"#00B42A"},
        {"name":"数据预测","start":"2023-06-15 12:30","end":"2023-06-15 14:15","color":"#FF7D00"},
        {"name":"报表生成","start":"2023-06-15 14:15","end":"2023-06-15 15:00","color":"#165DFF"}
    ]

# 波动指数
@router.get("/volatility-trend")
async def volatility_trend(
    days: int = 30,
    brand_id: int = 1,
    country: str = "cn",
    device: str = "iphone",
    session: AsyncSession = Depends(get_session),
):
    """
    返回整体排名波动率趋势。
    计算最近 days 天所有 app 的每日平均排名标准差，用于前端趋势图。
    """
    from datetime import timedelta, date
    days = max(1, min(days, 365))

    # 最近一次 chart_date
    latest_stmt = (
        select(func.max(AppStoreRankingDaily.chart_date))
        .where(
            AppStoreRankingDaily.brand_id == brand_id,
            AppStoreRankingDaily.country == country,
            AppStoreRankingDaily.device == device
        )
    )
    latest_date = (await session.execute(latest_stmt)).scalar_one_or_none()
    if not latest_date:
        return {"labels": [], "values": []}

    start_date = latest_date - timedelta(days=days - 1)

    # 查询每一天的排名标准差
    stmt = (
        select(
            AppStoreRankingDaily.chart_date,
            func.stddev_pop(AppStoreRankingDaily.ranking).label("stddev")
        )
        .where(
            AppStoreRankingDaily.chart_date >= start_date,
            AppStoreRankingDaily.chart_date <= latest_date,
            AppStoreRankingDaily.brand_id == brand_id,
            AppStoreRankingDaily.country == country,
            AppStoreRankingDaily.device == device,
            AppStoreRankingDaily.ranking.isnot(None)
        )
        .group_by(AppStoreRankingDaily.chart_date)
        .order_by(AppStoreRankingDaily.chart_date)
    )
    rows = await session.execute(stmt)
    rows = rows.all()

    labels = [r[0].isoformat() for r in rows]
    values = [round(float(r[1]), 2) if r[1] is not None else 0.0 for r in rows]

    return {"labels": labels, "values": values}

@router.get("/overview-kpis")
async def overview_kpis(
    brand_id: int = 1,          # 0=付费, 1=免费, 2=畅销
    country: str = "cn",
    device: str = "iphone",
    days: int = 30,
    session: AsyncSession = Depends(get_session),
):
    """
    返回核心指标：基于最近30天周期（或可配置days）与上一周期的对比统计。
    维度：brand_id / country / device；
    - new_entries: 当前周期存在但上一周期不存在的 app 数量
    - dropped_entries: 上一周期存在但当前周期不存在的 app 数量
    - top_genre: 当前周期中数量最多的 app_genre 及占比/数量
    - volatility_index: 最新日排名的总体波动（使用 ranking 的总体标准差 stddev_pop），保留两位小数
    """
    # 最近一次 chart_date
    latest_stmt = (
        select(func.max(AppStoreRankingDaily.chart_date))
        .where(
            AppStoreRankingDaily.brand_id == brand_id,
            AppStoreRankingDaily.country == country,
            AppStoreRankingDaily.device == device,
        )
    )
    latest_date = (await session.execute(latest_stmt)).scalar_one_or_none()
    if not latest_date:
        return {
            "latest_date": None,
            "period": {
                "current": {"start": None, "end": None},
                "previous": {"start": None, "end": None},
                "days": days,
            },
            "new_entries": 0,
            "dropped_entries": 0,
            "top_genre": {"name": None, "pct": 0.0, "apps": 0},
            "volatility_index": 0.0,
        }

    from datetime import timedelta

    # 定义时间窗口：当前周期与上一周期
    cur_start = latest_date - timedelta(days=days - 1)
    cur_end = latest_date
    prev_end = cur_start - timedelta(days=1)
    prev_start = prev_end - timedelta(days=days - 1)

    # 当前周期 app 集合
    cur_ids_stmt = (
        select(AppStoreRankingDaily.app_id)
        .where(
            AppStoreRankingDaily.chart_date >= cur_start,
            AppStoreRankingDaily.chart_date <= cur_end,
            AppStoreRankingDaily.brand_id == brand_id,
            AppStoreRankingDaily.country == country,
            AppStoreRankingDaily.device == device,
        )
        .distinct()
    )
    cur_ids = {row[0] for row in (await session.execute(cur_ids_stmt)).all()}

    # 上一周期 app 集合
    prev_ids_stmt = (
        select(AppStoreRankingDaily.app_id)
        .where(
            AppStoreRankingDaily.chart_date >= prev_start,
            AppStoreRankingDaily.chart_date <= prev_end,
            AppStoreRankingDaily.brand_id == brand_id,
            AppStoreRankingDaily.country == country,
            AppStoreRankingDaily.device == device,
        )
        .distinct()
    )
    prev_ids = {row[0] for row in (await session.execute(prev_ids_stmt)).all()}

    new_entries = len(cur_ids - prev_ids)
    dropped_entries = len(prev_ids - cur_ids)

    # 当前周期各类别占比
    genre_stmt = (
        select(AppStoreRankingDaily.app_genre, func.count().label("cnt"))
        .where(
            AppStoreRankingDaily.chart_date >= cur_start,
            AppStoreRankingDaily.chart_date <= cur_end,
            AppStoreRankingDaily.brand_id == brand_id,
            AppStoreRankingDaily.country == country,
            AppStoreRankingDaily.device == device,
        )
        .group_by(AppStoreRankingDaily.app_genre)
    )
    genre_rows = (await session.execute(genre_stmt)).all()
    genre_counts = {(g or "未知"): int(c) for (g, c) in genre_rows}
    cur_total = sum(genre_counts.values()) or 1
    if genre_counts:
        top_genre_name, top_genre_cnt = max(genre_counts.items(), key=lambda x: x[1])
    else:
        top_genre_name, top_genre_cnt = (None, 0)

    top_genre_pct = round(top_genre_cnt * 100.0 / cur_total, 1)

    # 最新日的整体波动指数：排名总体标准差（只用非空 ranking）
    vola_stmt = (
        select(func.stddev_pop(AppStoreRankingDaily.ranking))
        .where(
            AppStoreRankingDaily.chart_date == latest_date,
            AppStoreRankingDaily.brand_id == brand_id,
            AppStoreRankingDaily.country == country,
            AppStoreRankingDaily.device == device,
            AppStoreRankingDaily.ranking.isnot(None),
        )
    )
    vola_val = (await session.execute(vola_stmt)).scalar_one_or_none()
    volatility_index = round(float(vola_val), 2) if vola_val is not None else 0.0

    return {
        "latest_date": latest_date.isoformat(),
        "period": {
            "current": {"start": cur_start.isoformat(), "end": cur_end.isoformat()},
            "previous": {"start": prev_start.isoformat(), "end": prev_end.isoformat()},
            "days": days,
        },
        "new_entries": new_entries,
        "dropped_entries": dropped_entries,
        "top_genre": {"name": top_genre_name, "pct": top_genre_pct, "apps": top_genre_cnt},
        "volatility_index": volatility_index,
    }

from math import ceil

# —— 稳定 Top10 / 高波动 Top10 ——
# 说明：按最近 days 天（含 latest_date 向前回溯）的窗口，
# 使用 COALESCE(ranking, index) 作为“名次”进行统计，
# 计算每个 app 在窗口内的总体标准差（stddev_pop）与平均名次（avg_rank），
# 并可通过 min_presence 控制至少出现多少天才参与排名。

def _stability_base_stmt(days: int, brand_id: int, country: str, device: str, session: AsyncSession):
    # 最近一次 chart_date
    latest_stmt = (
        select(func.max(AppStoreRankingDaily.chart_date))
        .where(
            AppStoreRankingDaily.brand_id == brand_id,
            AppStoreRankingDaily.country == country,
            AppStoreRankingDaily.device == device,
        )
    )
    return latest_stmt

async def _stability_query(
    *,
    session: AsyncSession,
    days: int,
    brand_id: int,
    country: str,
    device: str,
    min_presence: int,
    order: str,          # 'stable' | 'volatile'
    limit: int,
):
    from datetime import timedelta

    latest_date = (await session.execute(
        _stability_base_stmt(days, brand_id, country, device, session)
    )).scalar_one_or_none()
    if not latest_date:
        return {"latest_date": None, "period": None, "items": []}

    start_date = latest_date - timedelta(days=days - 1)

    rank_expr = func.coalesce(AppStoreRankingDaily.ranking, AppStoreRankingDaily.index)

    stmt = (
        select(
            AppStoreRankingDaily.app_id.label("app_id"),
            func.max(AppStoreRankingDaily.app_name).label("app_name"),
            func.max(AppStoreRankingDaily.publisher).label("publisher"),
            func.max(AppStoreRankingDaily.app_genre).label("app_genre"),
            func.stddev_pop(rank_expr).label("stddev"),
            func.avg(rank_expr).label("avg_rank"),
            func.count(rank_expr).label("days_present"),
        )
        .where(
            AppStoreRankingDaily.chart_date >= start_date,
            AppStoreRankingDaily.chart_date <= latest_date,
            AppStoreRankingDaily.brand_id == brand_id,
            AppStoreRankingDaily.country == country,
            AppStoreRankingDaily.device == device,
            rank_expr.isnot(None),
        )
        .group_by(AppStoreRankingDaily.app_id)
        .having(func.count(rank_expr) >= min_presence)
    )

    # 排序：稳定=stddev 升序，其次 avg_rank 升序；高波动=stddev 降序，其次 avg_rank 升序
    if order == "volatile":
        stmt = stmt.order_by(func.stddev_pop(rank_expr).desc(), func.avg(rank_expr).asc())
    else:
        stmt = stmt.order_by(func.stddev_pop(rank_expr).asc(), func.avg(rank_expr).asc())

    stmt = stmt.limit(limit)

    rows = (await session.execute(stmt)).all()

    items = [
        {
            "app_id": r.app_id,
            "app_name": r.app_name,
            "publisher": r.publisher,
            "app_genre": r.app_genre,
            "stddev": round(float(r.stddev), 2) if r.stddev is not None else None,
            "avg_rank": round(float(r.avg_rank), 2) if r.avg_rank is not None else None,
            "days_present": int(r.days_present) if r.days_present is not None else 0,
        }
        for r in rows
    ]

    return {
        "latest_date": latest_date.isoformat(),
        "period": {"start": start_date.isoformat(), "end": latest_date.isoformat(), "days": days},
        "filters": {"brand_id": brand_id, "country": country, "device": device},
        "min_presence": min_presence,
        "items": items,
    }

@router.get("/stable-top10")
async def stable_top10(
    days: int = 30,
    brand_id: int = 1,          # 0=付费, 1=免费, 2=畅销
    country: str = "cn",
    device: str = "iphone",
    min_presence: int | None = None,  # 若未提供，则默认 ceil(days*0.6)
    limit: int = 10,
    session: AsyncSession = Depends(get_session),
):
    days = max(1, min(days, 365))
    limit = max(1, min(limit, 50))
    if min_presence is None:
        min_presence = ceil(days * 0.6)
    return await _stability_query(
        session=session,
        days=days,
        brand_id=brand_id,
        country=country,
        device=device,
        min_presence=min_presence,
        order="stable",
        limit=limit,
    )

@router.get("/volatile-top10")
async def volatile_top10(
    days: int = 30,
    brand_id: int = 1,          # 0=付费, 1=免费, 2=畅销
    country: str = "cn",
    device: str = "iphone",
    min_presence: int | None = None,  # 若未提供，则默认 ceil(days*0.6)
    limit: int = 10,
    session: AsyncSession = Depends(get_session),
):
    days = max(1, min(days, 365))
    limit = max(1, min(limit, 50))
    if min_presence is None:
        min_presence = ceil(days * 0.6)
    return await _stability_query(
        session=session,
        days=days,
        brand_id=brand_id,
        country=country,
        device=device,
        min_presence=min_presence,
        order="volatile",
        limit=limit,
    )
