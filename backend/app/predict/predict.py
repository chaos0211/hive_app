from datetime import date
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_session

router = APIRouter()

# predict.py（在文件末尾追加）
class ForecastReq(BaseModel):
    app_id: str
    country: str
    device: str
    brand: str
    lookback: int = Field(30, ge=7, le=120)
    horizon: int = Field(7, ge=1, le=30)

class ForecastPoint(BaseModel):
    d: date
    yhat: int
    lo: int
    hi: int

class ForecastResp(BaseModel):
    app_id: str
    country: str
    device: str
    brand: str
    history_last_date: Optional[date]
    points: List[ForecastPoint]

@router.post("/forecast", response_model=ForecastResp, summary="LSTM 趋势预测（返回未来 horizon 天）")
async def forecast_api(payload: ForecastReq, session: AsyncSession = Depends(get_session)):
    from app.predict.infer import forecast_app
    try:
        out = await forecast_app(session,
                                 app_id=payload.app_id, country=payload.country,
                                 device=payload.device, brand=payload.brand,
                                 lookback=payload.lookback, horizon=payload.horizon)
    except FileNotFoundError:
        # 模型未训练
        raise HTTPException(status_code=404, detail="model not found, please train it first")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return ForecastResp(
        app_id=payload.app_id,
        country=payload.country,
        device=payload.device,
        brand=payload.brand,
        history_last_date=out["history_last_date"],
        points=[ForecastPoint(**p) for p in out["forecast"]],
    )