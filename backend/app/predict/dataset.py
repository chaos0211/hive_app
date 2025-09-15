# backend/app/predict/dataset.py
from datetime import timedelta
from typing import List, Tuple, Dict, Any
import math

from sqlalchemy import select, asc
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.rating import AppRatings
from app.predict.consts import brand_key

MAX_RANK = 200  # 榜单长度，若不同榜单不同，可做成配置

def _dow_feats(d):
    # day-of-week one-cycle：sin/cos
    dow = d.weekday()  # 0..6
    return math.sin(2*math.pi*dow/7.0), math.cos(2*math.pi*dow/7.0)

async def fetch_series(session: AsyncSession, *, app_id: str, country: str, device: str, brand: str,
                       days: int) -> List[Dict[str, Any]]:
    """取最近 days 天的 (date, rank, genre, rating...)；按 update_time 升序"""
    rk = brand_key(brand)
    stmt = (select(AppRatings.update_time, getattr(AppRatings, rk), AppRatings.rating, AppRatings.rating_count)
            .where(AppRatings.app_id == app_id)
            .where(AppRatings.country == country)
            .where(AppRatings.device == device)
            .order_by(asc(AppRatings.update_time)))
    rows = await session.execute(stmt)
    rows = rows.all()
    if not rows:
        return []

    # 只保留最近 days 天
    end = rows[-1][0]
    start = end - timedelta(days=days-1)

    # 生成按天连续的日期索引
    raw = {r[0].date(): r for r in rows if start <= r[0] <= end}
    seq = []
    cur = start
    last_rank = None
    while cur <= end:
        rr = raw.get(cur)
        if rr:
            blob = rr[1] or {}
            rank = blob.get("ranking") if isinstance(blob, dict) else None
            rank = int(rank) if rank else None
            if not rank:   # 缺失就用上一个
                rank = last_rank
            else:
                last_rank = rank
            rating = rr[2]
            rating_count = rr[3]
        else:
            rank = last_rank
            rating = None
            rating_count = None

        seq.append({
            "d": cur, "rank": rank, "rating": rating, "rating_count": rating_count
        })
        cur += timedelta(days=1)
    return seq

def build_xy(seq: List[Dict[str, Any]], *, lookback: int, horizon: int) -> Tuple[List[List[List[float]]], List[List[float]], List]:
    """
    生成监督学习样本:
    X: [N, lookback, in_dim], y: [N, horizon], dates_of_y: [horizon dates per sample (最后一条就够推理)]
    """
    # 构特征
    xs, ys, dates = [], [], []
    # 规范化rank
    r_norm = []
    for item in seq:
        r = item["rank"] if item["rank"] else MAX_RANK
        r_norm.append(min(MAX_RANK, max(1, r))/MAX_RANK)

    for i in range(lookback, len(seq)-horizon+1):
        window = seq[i-lookback:i]
        # 特征：rank_norm, diff, dow(sin,cos)
        feats = []
        for j, w in enumerate(window):
            rn = r_norm[i-lookback+j]
            prev = r_norm[i-lookback+j-1] if j > 0 else rn
            diff = rn - prev
            s, c = _dow_feats(w["d"])
            feats.append([rn, diff, s, c])
        y = [r_norm[i+k] for k in range(horizon)]
        xs.append(feats)
        ys.append(y)
        dates.append([seq[i+k]["d"] for k in range(horizon)])
    return xs, ys, dates