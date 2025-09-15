from fastapi import APIRouter, Depends
from typing import Dict, List
from datetime import timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_session
from app.db.models.ranking import AppStoreRankingDaily

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])

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


# 类别热度趋势（趋势视图）
@router.get("/genre-trend")
async def genre_trend(
    days: int = 30,
    brand_id: int = 1,
    country: str = "cn",
    device: str = "iphone",
    genre: str = "all",    # 'all' 表示不限定类别
    session: AsyncSession = Depends(get_session),
):
    """
    类别热度趋势（趋势视图）：
    - 返回最近 days 天（含最新日）的日期 labels、每日上榜应用数量 app_count、每日平均排名 avg_rank。
    - 平均排名口径：同日同 app 取最好名次 MIN(COALESCE(ranking, index))，再对该日求 avg。
    - 当 `genre='all'` 时不限定类别；否则按给定 app_genre 过滤。
    """
    days = max(1, min(days, 365))

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
        return {"labels": [], "app_count": [], "avg_rank": []}

    from datetime import timedelta
    start_date = latest_date - timedelta(days=days - 1)

    # 公共过滤条件
    def _base_where():
        conds = [
            AppStoreRankingDaily.chart_date >= start_date,
            AppStoreRankingDaily.chart_date <= latest_date,
            AppStoreRankingDaily.brand_id == brand_id,
            AppStoreRankingDaily.country == country,
            AppStoreRankingDaily.device == device,
        ]
        if genre != "all":
            conds.append(AppStoreRankingDaily.app_genre == genre)
        return conds

    # 每日上榜应用数量（去重 app_id）
    app_cnt_stmt = (
        select(AppStoreRankingDaily.chart_date, func.count(func.distinct(AppStoreRankingDaily.app_id)))
        .where(*_base_where())
        .group_by(AppStoreRankingDaily.chart_date)
        .order_by(AppStoreRankingDaily.chart_date)
    )
    app_cnt_rows = (await session.execute(app_cnt_stmt)).all()
    app_cnt_map = {d.isoformat(): int(c) for d, c in app_cnt_rows}

    # 每日平均最好名次
    rank_expr = func.coalesce(AppStoreRankingDaily.ranking, AppStoreRankingDaily.index)
    best_per_app = (
        select(
            AppStoreRankingDaily.chart_date.label("chart_date"),
            AppStoreRankingDaily.app_id.label("app_id"),
            func.min(rank_expr).label("best_rank"),
        )
        .where(*(_base_where() + [rank_expr.isnot(None)]))
        .group_by(AppStoreRankingDaily.chart_date, AppStoreRankingDaily.app_id)
    ).subquery()

    avg_rank_stmt = (
        select(best_per_app.c.chart_date, func.avg(best_per_app.c.best_rank))
        .group_by(best_per_app.c.chart_date)
        .order_by(best_per_app.c.chart_date)
    )
    avg_rank_rows = (await session.execute(avg_rank_stmt)).all()
    avg_rank_map = {d.isoformat(): round(float(v), 2) for d, v in avg_rank_rows if v is not None}

    # 组装完整日期轴
    x_dates = [start_date + timedelta(days=i) for i in range(days)]
    labels = [d.isoformat() for d in x_dates]
    app_count = [app_cnt_map.get(lab, 0) for lab in labels]
    avg_rank = [avg_rank_map.get(lab, None) for lab in labels]

    return {"labels": labels, "app_count": app_count, "avg_rank": avg_rank}


# 各类别环比增长率（增长视图）
@router.get("/genre-growth")
async def genre_growth(
    days: int = 30,
    brand_id: int = 1,
    country: str = "cn",
    device: str = "iphone",
    genre: str = "all",
    session: AsyncSession = Depends(get_session),
):
    """
    各类别环比增长率（增长视图）：
    - 支持 `genre` 过滤：当 `genre!='all'` 时，仅统计该 app_genre；否则统计所有类别。
    - 以去重 app_id 数量为“热度”，对比当前周期 vs 上一周期，计算各类别增长率。
    - 返回 items: [{ genre, current_count, prev_count, growth }]
    """
    days = max(1, min(days, 365))

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
        return {"items": []}

    from datetime import timedelta
    cur_start = latest_date - timedelta(days=days - 1)
    cur_end = latest_date
    prev_end = cur_start - timedelta(days=1)
    prev_start = prev_end - timedelta(days=days - 1)

    # 当前周期：各类别去重 app 数
    cur_stmt = (
        select(AppStoreRankingDaily.app_genre, func.count(func.distinct(AppStoreRankingDaily.app_id)).label("cnt"))
        .where(
            AppStoreRankingDaily.chart_date >= cur_start,
            AppStoreRankingDaily.chart_date <= cur_end,
            AppStoreRankingDaily.brand_id == brand_id,
            AppStoreRankingDaily.country == country,
            AppStoreRankingDaily.device == device,
            *( [AppStoreRankingDaily.app_genre == genre] if genre != "all" else [] ),
        )
        .group_by(AppStoreRankingDaily.app_genre)
    )
    cur_rows = (await session.execute(cur_stmt)).all()
    cur_map = {(g or "未知"): int(c) for g, c in cur_rows}

    # 上一周期：各类别去重 app 数
    prev_stmt = (
        select(AppStoreRankingDaily.app_genre, func.count(func.distinct(AppStoreRankingDaily.app_id)).label("cnt"))
        .where(
            AppStoreRankingDaily.chart_date >= prev_start,
            AppStoreRankingDaily.chart_date <= prev_end,
            AppStoreRankingDaily.brand_id == brand_id,
            AppStoreRankingDaily.country == country,
            AppStoreRankingDaily.device == device,
            *( [AppStoreRankingDaily.app_genre == genre] if genre != "all" else [] ),
        )
        .group_by(AppStoreRankingDaily.app_genre)
    )
    prev_rows = (await session.execute(prev_stmt)).all()
    prev_map = {(g or "未知"): int(c) for g, c in prev_rows}

    # 合并键并计算增长率
    all_genres = set(cur_map.keys()) | set(prev_map.keys())
    items = []
    for g in sorted(all_genres):
        cur = cur_map.get(g, 0)
        prev = prev_map.get(g, 0)
        if prev > 0:
            growth = round((cur - prev) * 100.0 / prev, 1)
        else:
            growth = 100.0 if cur > 0 else 0.0
        items.append({
            "genre": g,
            "current_count": cur,
            "prev_count": prev,
            "growth": growth,
        })

    # 默认按增长率降序排序
    items.sort(key=lambda x: x["growth"], reverse=True)
    return {"items": items}

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


@router.get("/genres")
async def list_genres(
    days: int = 30,
    brand_id: int = 1,
    country: str = "cn",
    device: str = "iphone",
    session: AsyncSession = Depends(get_session),
):
    """
    返回最近 days 天内（含最新日），在指定 brand_id/country/device 下出现过的 app_genre（中文），
    按去重 app_id 数量从高到低排序。只返回字符串数组。
    """
    # 找最近一次榜单日期
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
        return {"items": []}

    from datetime import timedelta
    start_date = latest_date - timedelta(days=max(1, min(days, 365)) - 1)

    # 统计各类别热度（按去重 app_id）
    stmt = (
        select(
            AppStoreRankingDaily.app_genre,
            func.count(func.distinct(AppStoreRankingDaily.app_id)).label("cnt"),
        )
        .where(
            AppStoreRankingDaily.chart_date >= start_date,
            AppStoreRankingDaily.chart_date <= latest_date,
            AppStoreRankingDaily.brand_id == brand_id,
            AppStoreRankingDaily.country == country,
            AppStoreRankingDaily.device == device,
            AppStoreRankingDaily.app_genre.isnot(None),
            AppStoreRankingDaily.app_genre != "",
        )
        .group_by(AppStoreRankingDaily.app_genre)
        .order_by(func.count(func.distinct(AppStoreRankingDaily.app_id)).desc())
    )
    rows = (await session.execute(stmt)).all()
    items = [g for g, _ in rows]
    return {"items": items}

# ——— 特征重要性热力图数据（单列） ———
from collections import defaultdict

@router.get("/feature-importance")
async def feature_importance(
    days: int = 30,
    brand_id: int = 1,
    country: str = "cn",
    device: str = "iphone",
    session: AsyncSession = Depends(get_session),
):
    """
    特征重要性热力图数据（单列）：
    - 目标变量：`index`（应用榜单名次，使用 index，**不使用 ranking**）。
    - 统计窗口：最近 days 天（含最新日），按 brand_id/country/device 过滤；**不含类别筛选**。
    - 特征维度：country/device/brand（各自 one-hot 二值特征）；以及窗口内出现过的每个 genre（one-hot 二值特征）。
      例如：country=cn, device=iphone, brand=paid(0), brand=free(1), genre=<<g>>（每个 genre）。
    - 重要性口径：每个二值特征（flag）按 {0,1} 分组，计算组间方差占比 R^2；若 raw R^2 为 0（或非常接近0），直接跳过不返回。
    - 返回 features/scores/raw_scores 顺序一一对应，均为非零维度（四位小数）。
    返回：
      {
        "features": ["country=cn","device=iphone","brand=paid(0)","brand=free(1)","genre=游戏",...],
        "scores":   [0.41, 0.27, ...],     # 0~1 归一化后的相对重要性（按本口径计算）
        "raw_scores": [0.28, 0.18, ...],   # 原始 R^2（组间方差占全局方差的占比）
        "meta": { "n_samples": 1234, "latest_date": "YYYY-MM-DD", "days": 30 }
      }
    """
    from datetime import timedelta
    from collections import defaultdict

    days = max(1, min(days, 365))

    # 1) 最近一次 chart_date（按维度过滤）
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
        return {"features": [], "scores": [], "raw_scores": [], "meta": {"n_samples": 0, "latest_date": None, "days": days}}

    start_date = latest_date - timedelta(days=days - 1)

    # 2) 拉取窗口内所需字段，目标变量使用 index（忽略 ranking）
    q = (
        select(
            AppStoreRankingDaily.index,          # 目标
            AppStoreRankingDaily.app_genre,      # 维度：genre
            AppStoreRankingDaily.brand_id,       # 维度：brand
            AppStoreRankingDaily.country,        # 维度：country
            AppStoreRankingDaily.device,         # 维度：device
            AppStoreRankingDaily.is_ad,          # 保留以备后续扩展
            AppStoreRankingDaily.price,          # 保留以备后续扩展
        )
        .where(
            AppStoreRankingDaily.chart_date >= start_date,
            AppStoreRankingDaily.chart_date <= latest_date,
            AppStoreRankingDaily.brand_id == brand_id,
            AppStoreRankingDaily.country == country,
            AppStoreRankingDaily.device == device,
            AppStoreRankingDaily.index.isnot(None),
        )
    )
    rows = (await session.execute(q)).all()
    if not rows:
        return {"features": [], "scores": [], "raw_scores": [], "meta": {"n_samples": 0, "latest_date": latest_date.isoformat(), "days": days}}

    # 3) 准备样本
    y = []               # index list
    genres = []
    brands = []
    countries = []
    devices = []
    # —— 价格衍生特征 ——
    # 额外收集 is_free 和 price_bins
    for idx, genre_val, brand_val, country_val, device_val, is_ad_val, price_val in rows:
        try:
            y_val = int(idx) if idx is not None else None
        except Exception:
            y_val = None
        if y_val is None:
            continue
        y.append(y_val)
        genres.append(genre_val or "未知")
        brands.append(int(brand_val))
        countries.append(country_val or '')
        devices.append(device_val or '')
        # —— 价格衍生特征 ——
        # 转为 float；None/异常按 0 处理
        try:
            price_f = float(price_val) if price_val is not None else 0.0
        except Exception:
            price_f = 0.0
        # 是否免费
        # 注意：畅销榜/付费榜里 is_free 不是常量；免费榜可能是常量（会在后续 R^2 过滤掉）
        # True->1, False->0
        if 'is_free_list' not in locals():
            is_free_list = []
        is_free_list.append(1 if price_f == 0.0 else 0)

        # 价格分箱（右闭区间）：(0,1], (1,5], (5,20], (20, +∞)
        # 免费（==0）不落入这些箱子，仅由 is_free 覆盖
        if 'price_bin_tags' not in locals():
            price_bin_tags = []  # 保存箱标签顺序
        if 'price_bin_list' not in locals():
            price_bin_list = []  # 每个样本一个字符串标签
        if price_f == 0.0:
            price_bin = 'free'
        elif 0.0 < price_f <= 1.0:
            price_bin = '(0,1]'
        elif price_f <= 5.0:
            price_bin = '(1,5]'
        elif price_f <= 20.0:
            price_bin = '(5,20]'
        else:
            price_bin = '(20,∞)'
        price_bin_list.append(price_bin)

    n = len(y)
    if n == 0:
        return {"features": [], "scores": [], "raw_scores": [], "meta": {"n_samples": 0, "latest_date": latest_date.isoformat(), "days": days}}

    # 4) 计算全局均值与方差
    mu = sum(y) / n
    var = sum((v - mu) ** 2 for v in y) / n
    if var <= 1e-12:
        return {
            "features": [],
            "scores": [],
            "raw_scores": [],
            "meta": {"n_samples": n, "latest_date": latest_date.isoformat(), "days": days},
        }

    # —— 构造候选二值维度特征 ——
    feat_bins: dict[str, list[int]] = {}
    # 固定维度（按当前数据值做 one-hot；常量会得到 0 R^2 并被过滤）
    feat_bins["country=cn"]   = [1 if c == 'cn' else 0 for c in countries]
    feat_bins["device=iphone"] = [1 if d == 'iphone' else 0 for d in devices]
    feat_bins["brand=paid(0)"] = [1 if b == 0 else 0 for b in brands]
    feat_bins["brand=free(1)"] = [1 if b == 1 else 0 for b in brands]
    # 动态维度：针对窗口内出现过的所有类别，逐个构造 one-hot 维度
    distinct_genres = sorted({g or '未知' for g in genres})
    for g in distinct_genres:
        feat_bins[f"genre={g}"] = [1 if (gg or '未知') == g else 0 for gg in genres]

    # —— 价格相关二值特征 ——
    # 1) is_free
    if 'is_free_list' in locals():
        feat_bins['is_free=1'] = list(is_free_list)
    # 2) price bins（将每个出现过的价位段做成 one-hot 二值特征）
    if 'price_bin_list' in locals():
        distinct_bins = sorted(set(price_bin_list))
        for tag in distinct_bins:
            if tag == 'free':
                continue  # 免费用 is_free=1 覆盖
            feat_bins[f'price∈{tag}'] = [1 if b == tag else 0 for b in price_bin_list]

    # R^2 计算（按二值特征分组）
    def r2_binary(bin_vals: list[int]) -> float:
        groups = defaultdict(list)
        for xi, yi in zip(bin_vals, y):
            groups[str(int(1 if xi else 0))].append(yi)
        between = 0.0
        for vals in groups.values():
            if not vals:
                continue
            ng = len(vals)
            mug = sum(vals) / ng
            between += (ng / n) * (mug - mu) ** 2
        return max(0.0, min(1.0, between / var))

    # 计算并收集非零（按两位小数四舍五入后）维度
    disp_names: list[str] = []
    kept_raw: list[float] = []
    for name, bin_vals in feat_bins.items():
        r = r2_binary(bin_vals)
        # 两位小数四舍五入
        r_2 = round(r, 2)
        if r_2 <= 0.0:
            continue  # 0.00 不展示
        # 展示名：genre=休闲 -> 休闲；其他维度名称保持原样
        if name.startswith("genre="):
            show_name = name.split("=", 1)[1]
        else:
            show_name = name
        disp_names.append(show_name)
        kept_raw.append(r)  # 归一化用未四舍五入的原始值

    # 归一化和返回
    if not kept_raw:
        return {"features": [], "scores": [], "raw_scores": [], "meta": {"n_samples": n, "latest_date": latest_date.isoformat(), "days": days}}

    s = sum(kept_raw)
    if s > 0:
        scores = [round(v / s, 2) for v in kept_raw]
    else:
        scores = [0.0 for _ in kept_raw]

    raw_scores = [round(v, 2) for v in kept_raw]

    return {
        "features": disp_names,
        "scores": scores,
        "raw_scores": raw_scores,
        "meta": {"n_samples": n, "latest_date": latest_date.isoformat(), "days": days}
    }