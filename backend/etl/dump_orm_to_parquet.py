#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 MySQL 的 app_ratings 按 chart_date -> pt=YYYY-MM-DD 分区，导出到
/Users/chaos/data/lake/hive_app/ods_app_ratings/pt=.../*.parquet

依赖：
  pip install sqlalchemy pandas pyarrow sqlalchemy-utils pymysql
"""

import os
import argparse
from datetime import date
import pandas as pd
from sqlalchemy import create_engine, text

# ---- 配置区 ----
# 注意：如果你项目里的 DATABASE_URL 是 async 驱动（mysql+aiomysql://），
# 这里需要换成 sync 驱动（mysql+pymysql://）才能给 pandas 用。

DEFAULT_DB_URL = "mysql+pymysql://root:123456@127.0.0.1:33309/hive_app?charset=utf8mb4"
DEFAULT_OUT_ROOT = "/Users/chaos/data/lake/hive_app/ods_app_ratings"
DEFAULT_TABLE = "app_ratings"
DEFAULT_CHUNK = 100_000  # 分批导出，避免一次性吃内存


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--table", default=DEFAULT_TABLE, help="表名，默认 app_ratings")
    ap.add_argument("--since", default=None, help="仅导出 chart_date >= since 的数据（YYYY-MM-DD），可选")
    ap.add_argument("--out", default=DEFAULT_OUT_ROOT, help="Parquet 输出根目录")
    ap.add_argument("--chunk", type=int, default=DEFAULT_CHUNK, help="每批次行数")
    return ap.parse_args()


def ensure_dir(p):
    os.makedirs(p, exist_ok=True)


def main():
    args = parse_args()
    engine = create_engine(DEFAULT_DB_URL)

    # WHERE 条件
    where = ""
    params = {}
    if args.since:
        where = "WHERE chart_date >= :since"
        params["since"] = args.since

    # 先取所有不同的 chart_date（按天导出，确保 pt 目录规范）
    with engine.begin() as conn:
        rs = conn.execute(
            text(f"SELECT DISTINCT chart_date FROM {args.table} {where} ORDER BY chart_date")
            , params
        )
        dates = [r[0] for r in rs]  # datetime.date

    total_rows = 0
    for d in dates:
        pt = d.strftime("%Y-%m-%d") if isinstance(d, date) else str(d)
        out_dir = os.path.join(args.out, f"pt={pt}")
        ensure_dir(out_dir)

        # 分批导出当前这一天的数据
        offset = 0
        batch_idx = 0
        while True:
            sql = text(
                f"""
                SELECT
                    id, app_id, app_name, publisher, country, brand, device,
                    chart_date, last_release_time, update_time,
                    `index`, genre, keyword_cover, keyword_cover_top3,
                    rank_a, rank_b, rank_c, rating, rating_num, is_ad, icon_url, raw_json
                FROM {args.table}
                WHERE chart_date = :d
                ORDER BY id
                LIMIT :limit OFFSET :offset
                """
            )
            with engine.begin() as conn:
                df = pd.read_sql(sql, conn, params={"d": d, "limit": args.chunk, "offset": offset})

            if df.empty:
                break

            # 写到单独文件，避免覆盖；基于 batch_idx 命名
            out_file = os.path.join(out_dir, f"part-{batch_idx:05d}.parquet")
            df.to_parquet(out_file, index=False)  # 需要 pyarrow

            rows = len(df)
            total_rows += rows
            offset += rows
            batch_idx += 1
            print(f"[{pt}] wrote {rows} rows -> {out_file}")

    print(f"[DONE] exported {total_rows} rows into {args.out}")


if __name__ == "__main__":
    main()