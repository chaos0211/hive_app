# backend/app/predict/infer.py
from datetime import timedelta
import torch
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.db.models.rating import AppRatings
from app.predict.models.lstm import RankLSTM
from app.predict.dataset import fetch_series, build_xy, _dow_feats, MAX_RANK
from app.predict.io import load_model, model_path

async def latest_date(session: AsyncSession, *, country: str, device: str, brand: str):
    stmt = (select(AppRatings.update_time)
            .where(AppRatings.country==country, AppRatings.device==device, AppRatings.brand==brand)
            .order_by(desc(AppRatings.update_time)).limit(1))
    r = await session.execute(stmt)
    row = r.first()
    return row[0].date() if row else None

async def forecast_app(session: AsyncSession, *, app_id: str, country: str, device: str, brand: str,
                       lookback: int, horizon: int):
    # 加载模型
    path = model_path(app_id, country, device, brand)
    state = load_model(path)  # 若不存在会抛异常，接口层捕获
    meta = state["meta"]
    model = RankLSTM(in_dim=meta["in_dim"], horizon=meta["horizon"])
    model.load_state_dict(state["state_dict"])
    model.eval()

    # 最近 lookback 天历史
    days_needed = lookback + 1
    seq = await fetch_series(session, app_id=app_id, country=country, device=device, brand=brand, days=days_needed)
    if len(seq) < lookback:
        raise RuntimeError("not enough history for inference")

    xs, _, _ = build_xy(seq, lookback=lookback, horizon=1)  # 只要最后一个窗口
    import numpy as np
    x = torch.tensor(np.array(xs[-1:]), dtype=torch.float32)  # [1, lookback, in_dim]

    with torch.no_grad():
        yhat = model(x)[0].tolist()  # [horizon], 预测的是 rank_norm

    # 还原名次（简单反归一化）
    preds = [max(1, int(round(p * MAX_RANK))) for p in yhat]

    # 生成未来日期
    last_date = (await latest_date(session, country=country, device=device, brand=brand))
    start = last_date + timedelta(days=1)
    future_dates = [start + timedelta(days=i) for i in range(horizon)]

    # 简单置信区间（经验：±5名，可用历史残差改进）
    lo = [max(1, v-5) for v in preds]
    hi = [v+5 for v in preds]

    return {
        "history_last_date": last_date,
        "forecast": [{"d": future_dates[i], "yhat": preds[i], "lo": lo[i], "hi": hi[i]} for i in range(horizon)]
    }