from datetime import date, timedelta, datetime
from typing import List, Optional
import json
import os
from pathlib import Path
import hashlib
import re
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import select, func, text, asc, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.db.base import get_session
from app.db.models.rating import AppRatings
from app.predict.api.service import forecast_global as svc_forecast_global


router = APIRouter(prefix="/api/v1/predict", tags=["predict"])

# ----------------------------
# Pydantic Schemas
# ----------------------------

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

def _brand_key(brand: Optional[str]) -> Optional[str]:
    if not brand:
        return None
    m = {"free": "rank_a", "paid": "rank_b", "grossing": "rank_c"}
    b = (brand or "").lower()
    return m.get(b)

# Map English brand to Chinese label
def _brand_cn(b: Optional[str]) -> Optional[str]:
    if not b:
        return b
    m = {"free": "免费", "paid": "付费", "grossing": "畅销"}
    return m.get(b.lower(), b)

def _json_change(blob) -> Optional[int]:
    """Safely extract `change` from rank_a/b/c which may be JSON string or dict."""
    if blob is None:
        return None
    if isinstance(blob, dict):
        try:
            v = blob.get("change")
            return int(v) if v is not None else None
        except Exception:
            return None
    # try parse as json string
    try:
        obj = json.loads(blob)
        v = obj.get("change")
        return int(v) if v is not None else None
    except Exception:
        return None

_MODEL_RE = re.compile(r"^(?:global_)?(?P<country>[a-z]{2})_(?P<device>iphone|ipad)_(?P<brand>free|paid|grossing)_(?:[a-z]+)(?:_\d+)?\.pt$", re.IGNORECASE)

def _parse_model_name(model_name: str) -> tuple[str, str, str]:
    """Extract (country, device, brand) from a model filename, e.g.
    global_us_iphone_free_lstm.pt or global_cn_iphone_free_lstm_20250917202635.pt
    """
    if not model_name:
        raise ValueError("model_name required for this operation")
    m = _MODEL_RE.match(model_name)
    if not m:
        raise HTTPException(status_code=400, detail=f"invalid model_name format: {model_name}")
    gd = m.groupdict()
    return gd["country"].lower(), gd["device"].lower(), gd["brand"].lower()

async def _latest_date(
    session: AsyncSession,
    *,
    country: str,
    device: str,
    brand: Optional[str] = None
) -> Optional[date]:
    """
    获取给定过滤条件下的最新 update_time（最近一次抓取日期）。
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
# Model File Helpers
# ----------------------------
ALGO_EXTS = {
    "lstm": [".pt"],
}

def _app_root() -> Path:
    # backend/app/api/v1/predict.py -> go up to backend/app
    return Path(__file__).resolve().parents[2]

def _models_root() -> Path:
    return _app_root() / "predict" / "models"

def _legacy_models_root() -> Path:
    # legacy training outputs live in backend/models/<algo>
    # this returns backend/models
    return _app_root().parent / "models"

def _legacy_algo_dir(algo: str) -> Path:
    return _legacy_models_root() / algo

def _algo_dir(algo: str) -> Path:
    return _models_root() / algo

def _upload_dir() -> Path:
    return _models_root() / "upload"

def _ensure_dirs(*dirs: Path) -> None:
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

def _sanitize_filename(name: str) -> str:
    # Avoid path traversal and keep simple ASCII-ish names
    bad = set('/\\\0')
    cleaned = ''.join(ch for ch in name if ch not in bad)
    if not cleaned:
        cleaned = f"model_{int(datetime.utcnow().timestamp())}"
    return cleaned

def _list_files(dirpath: Path, exts: list[str]) -> list[str]:
    if not dirpath.exists():
        return []
    files = []
    for p in sorted(dirpath.iterdir()):
        if p.is_file() and p.suffix.lower() in exts:
            files.append(p.name)
    return files


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


@router.post("/forecast_global", summary="根据模型对指定应用进行趋势预测（受筛选与模型选择影响）")
async def forecast_global_api(
    app_id: str,
    country: str,
    device: str,
    brand: str,
    genre: Optional[str] = Query(None, description="rank_c.genre，可选；为空时后端自动推断"),
    lookback: int = Query(30, ge=7, le=120),
    horizon: int = Query(7, ge=1, le=90),
    model_source: Optional[str] = Query(None, description="upload 或 trained；决定模型所在目录"),
    model_name: Optional[str] = Query(None, description="模型文件名，例如 global_us_iphone_free_lstm.pt"),
    session: AsyncSession = Depends(get_session),
):
    preds = await svc_forecast_global(
        session,
        country=country,
        device=device,
        brand=brand,
        app_id=app_id,
        lookback=lookback,
        horizon=horizon,
        model_source=model_source,
        model_name=model_name,
        genre=genre,
    )
    return {
        "app_id": app_id,
        "country": country,
        "device": device,
        "brand": brand,
        "genre": genre,
        "lookback": lookback,
        "horizon": horizon,
        "model_source": model_source,
        "model_name": model_name,
        "predictions": preds,
    }


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

    rk = _brand_key(brand)
    cols = [
        AppRatings.index,
        AppRatings.app_id,
        AppRatings.app_name,
        AppRatings.publisher,
        AppRatings.icon_url,
    ]
    if rk:
        cols.append(getattr(AppRatings, rk).label("rank_json"))

    stmt = (
        select(*cols)
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
    for row in rows.all():
        # row fields: when rk present -> (index, app_id, app_name, publisher, icon_url, rank_json)
        idx = row[0]; app_id_v = row[1]; app_name = row[2]; publisher = row[3]; icon_url = row[4]
        change_val = None
        if rk:
            rank_json = row[5]
            change_val = _json_change(rank_json)
        items.append(
            TopNItem(
                rank=int(idx) if idx is not None else 999999,
                app_id=str(app_id_v),
                app_name=app_name,
                publisher=publisher,
                icon_url=icon_url,
                change=change_val,
                change_percent=None,
            )
        )

    return TopNResponse(date=latest, brand=brand or "", country=country, device=device, items=items)


@router.get("/topn/predict", response_model=TopNResponse, summary="使用模型预测 TopN（仅受模型选择影响）")
async def topn_predict(
    model_name: str = Query(..., description="模型文件名，如 global_us_iphone_free_lstm.pt"),
    model_source: Optional[str] = Query(None, description="upload 或 trained；决定模型所在目录"),
    n: int = Query(10, ge=1, le=50),
    lookback: int = Query(30, ge=7, le=120),
    horizon: int = Query(1, ge=1, le=90, description="用于排序的预测步长（7/30/90 等）"),
    target: Optional[date] = Query(None, description="预测目标日期；默认=最新日期的下一天"),
    session: AsyncSession = Depends(get_session),
):
    # 从模型名解析出分区
    country, device, brand = _parse_model_name(model_name)
    brand_cn = _brand_cn(brand)
    latest = await _latest_date(session, country=country, device=device, brand=brand)
    if not latest:
        return TopNResponse(date=date.today(), brand=brand_cn or "", country=country, device=device, items=[])

    # 预测日期默认为 latest 的下一天；基准（用于变化对比）使用 latest 当天的实际 index
    pred_date = (target or (latest + timedelta(days=1)))
    baseline_date = latest

    # 先取最近一天该分区的前 n*3 个候选（减少推理量的同时保留竞争）
    candidate_k = max(n * 3, 30)
    stmt = (
        select(AppRatings.app_id, AppRatings.index, AppRatings.app_name, AppRatings.publisher, AppRatings.icon_url)
        .where(AppRatings.country == country)
        .where(AppRatings.device == device)
        .where(AppRatings.brand == brand)
        .where(AppRatings.update_time == latest)
        .order_by(asc(AppRatings.index))
        .limit(candidate_k)
    )
    rows = (await session.execute(stmt)).all()
    if not rows:
        return TopNResponse(date=pred_date, brand=brand_cn or "", country=country, device=device, items=[])

    # 对候选逐个做一次 horizon 预测，拿第 horizon 天的预测名次进行排序
    scored: list[tuple[int, str, str, str, str, Optional[int]]] = []  # (pred_rank, app_id, app_name, publisher, icon_url, baseline_idx)
    for app_id_v, cur_idx, app_name, publisher, icon_url in rows:
        preds = await svc_forecast_global(
            session,
            country=country,
            device=device,
            brand=brand,
            app_id=str(app_id_v),
            lookback=lookback,
            horizon=max(1, horizon),
            model_source=model_source,
            model_name=model_name,
            genre=None,
        )
        if not preds:
            continue
        idx = min(len(preds), max(1, horizon)) - 1  # horizon-th step, safe
        pred_rank = int(preds[idx])
        baseline_idx = int(cur_idx) if cur_idx is not None else None
        scored.append((pred_rank, str(app_id_v), app_name, publisher, icon_url, baseline_idx))

    # 按预测名次升序排序
    scored.sort(key=lambda x: x[0])

    items: list[TopNItem] = []
    for disp_rank, (pred_rank, app_id_v, app_name, publisher, icon_url, base_idx) in enumerate(scored[:n], start=1):
        change_val: Optional[int] = None
        change_pct: Optional[float] = None
        if base_idx is not None and base_idx > 0:
            change_val = int(base_idx) - int(pred_rank)  # 正=上升（实际index -> 预测名次）
            try:
                change_pct = round(change_val / float(base_idx) * 100.0, 4)
            except Exception:
                change_pct = None
        items.append(TopNItem(
            rank=int(disp_rank),  # 左侧展示位次 1..N
            app_id=str(app_id_v),
            app_name=app_name,
            publisher=publisher,
            icon_url=icon_url,
            change=change_val,
            change_percent=change_pct,
        ))

    return TopNResponse(date=pred_date, brand=brand_cn or "", country=country, device=device, items=items)


@router.get("/models", summary="列出本地可用的模型文件（按算法）")
async def list_models(
    algo: str = Query("lstm", description="算法类型，目前支持：lstm"),
    include_uploaded: bool = Query(True, description="是否包含上传目录的模型文件"),
):
    algo = (algo or "").lower()
    if algo not in ALGO_EXTS:
        raise HTTPException(status_code=400, detail=f"unsupported algo: {algo}")
    exts = [e.lower() for e in ALGO_EXTS[algo]]

    # directories
    root = _models_root()
    d_algo = _algo_dir(algo)
    d_upload = _upload_dir()
    legacy_root = _legacy_models_root()
    legacy_algo = _legacy_algo_dir(algo)
    _ensure_dirs(root, d_algo, d_upload)

    trained = _list_files(d_algo, exts)
    legacy = _list_files(legacy_algo, exts)
    uploaded = _list_files(d_upload, exts) if include_uploaded else []

    merged = list(dict.fromkeys(trained + legacy + (uploaded if include_uploaded else [])))
    out = {
        "algo": algo,
        "root": str(root),
        "legacy_root": str(legacy_root),
        "dirs": {
            "trained": str(d_algo),
            "legacy_trained": str(legacy_algo),
            "uploaded": str(d_upload),
        },
        "files": merged,
        "groups": {
            "trained": trained,
            "legacy_trained": legacy,
            "uploaded": uploaded,
        },
        "count": {
            "trained": len(trained),
            "legacy_trained": len(legacy),
            "uploaded": len(uploaded),
            "total": len(merged),
        },
    }
    return JSONResponse(content=out)


@router.post("/models/upload", summary="上传模型文件到 upload 目录")
async def upload_model(
    algo: str = Query("lstm", description="算法类型，目前支持：lstm"),
    file: UploadFile = File(..., description="模型文件，扩展名需匹配算法类型，如 .pt"),
    max_bytes: int = Query(300 * 1024 * 1024, ge=1, description="最大允许大小（字节），默认 300MB"),
):
    algo = (algo or "").lower()
    if algo not in ALGO_EXTS:
        raise HTTPException(status_code=400, detail=f"unsupported algo: {algo}")
    allowed_exts = [e.lower() for e in ALGO_EXTS[algo]]
    # Validate extension
    orig_name = file.filename or ""
    ext = Path(orig_name).suffix.lower()
    if ext not in allowed_exts:
        raise HTTPException(status_code=400, detail=f"invalid file extension: {ext}; allowed: {allowed_exts}")

    # Prepare target path
    root = _models_root()
    d_upload = _upload_dir()
    _ensure_dirs(root, d_upload)

    # Sanitize filename and avoid overwrite by adding timestamp if exists
    base = _sanitize_filename(Path(orig_name).name)
    target = d_upload / base
    if target.exists():
        ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        target = d_upload / f"{Path(base).stem}_{ts}{ext}"

    # Stream save with size limit & SHA256
    hasher = hashlib.sha256()
    size = 0
    try:
        with target.open("wb") as f:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                size += len(chunk)
                if size > max_bytes:
                    try:
                        f.close()
                        target.unlink(missing_ok=True)
                    finally:
                        pass
                    raise HTTPException(status_code=413, detail=f"file too large: {size} > {max_bytes}")
                hasher.update(chunk)
                f.write(chunk)
    finally:
        await file.close()

    return JSONResponse(content={
        "algo": algo,
        "saved_as": target.name,
        "dir": str(d_upload),
        "bytes": size,
        "sha256": hasher.hexdigest(),
    })
