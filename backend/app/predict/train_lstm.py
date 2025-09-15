# backend/app/predict/train_lstm.py
import argparse, asyncio
import torch, torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.predict.dataset import fetch_series, build_xy
from app.predict.models.lstm import RankLSTM
from app.predict.io import model_path, save_model

def to_tensors(xs, ys):
    import numpy as np
    X = torch.tensor(np.array(xs), dtype=torch.float32)
    Y = torch.tensor(np.array(ys), dtype=torch.float32)
    return X, Y

async def _amain(args):
    from app.db.base import DATABASE_URL
    engine = create_async_engine(DATABASE_URL, future=True)
    Session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with Session() as session:
        total_days = args.lookback + args.horizon + args.extra_days
        seq = await fetch_series(session, app_id=args.app_id, country=args.country, device=args.device, brand=args.brand, days=total_days)
        if len(seq) < args.lookback + args.horizon + 5:
            raise RuntimeError("data too short for training")

    xs, ys, _ = build_xy(seq, lookback=args.lookback, horizon=args.horizon)
    X, Y = to_tensors(xs, ys)
    ds = TensorDataset(X, Y)
    dl = DataLoader(ds, batch_size=args.batch, shuffle=True)

    model = RankLSTM(in_dim=X.shape[-1], hidden=args.hidden, layers=args.layers, horizon=args.horizon, dropout=args.dropout)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr)
    loss_fn = nn.L1Loss()  # MAE

    model.train()
    for epoch in range(1, args.epochs+1):
        total = 0.0
        for xb, yb in dl:
            opt.zero_grad()
            pred = model(xb)
            loss = loss_fn(pred, yb)
            loss.backward()
            opt.step()
            total += loss.item() * xb.size(0)
        print(f"epoch {epoch}/{args.epochs} - mae: {total/len(ds):.4f}")

    path = model_path(args.app_id, args.country, args.device, args.brand)
    save_model(path, {
        "state_dict": model.state_dict(),
        "meta": {"in_dim": X.shape[-1], "horizon": args.horizon, "lookback": args.lookback}
    })
    print(f"saved: {path}")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--db", required=True, help="async DB url, e.g. mysql+aiomysql://user:pwd@host/dbname")
    p.add_argument("--app_id", required=True)
    p.add_argument("--country", required=True)
    p.add_argument("--device", required=True, choices=["iphone","ipad","android"])
    p.add_argument("--brand", required=True, choices=["free","paid","grossing"])
    p.add_argument("--lookback", type=int, default=30)
    p.add_argument("--horizon", type=int, default=7)
    p.add_argument("--extra_days", type=int, default=60, help="额外历史天数，便于形成足够样本")
    p.add_argument("--epochs", type=int, default=50)
    p.add_argument("--batch", type=int, default=32)
    p.add_argument("--hidden", type=int, default=64)
    p.add_argument("--layers", type=int, default=2)
    p.add_argument("--dropout", type=float, default=0.1)
    p.add_argument("--lr", type=float, default=1e-3)
    args = p.parse_args()
    asyncio.run(_amain(args))

if __name__ == "__main__":
    main()