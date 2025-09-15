#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Qimai Top Charts Crawler (CN/iPhone)
- 抓取过去一年的 3 个榜单（brand_id: 0付费 / 1免费 / 2畅销）
- 每天最多抓取 5 页（Top 200；20 条/页）
- 必传单一分类：--genre（默认 36）
- 内置重试&限速；可选是否保存原始响应/扁平JSONL
- 直接调用 ranking_service.upsert_page() 批量写入 MySQL（幂等）
用法：
  python qimai_crawl.py --start 2024-08-25 --end 2025-08-24 --genre 36 --brands 0 1 2 --max_pages 5
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Ensure we can import `app` when running this script from any directory
from pathlib import Path
_HERE = Path(__file__).resolve()
_BACKEND_DIR = _HERE.parents[2]  # .../hive_app/backend
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

import requests
from app.services.ranking_service import upsert_page
import logging

BASE_URL = "https://api.qimai.cn/rank/indexPlus/brand_id/{brand_id}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
}

SESSION = requests.Session()
SESSION.headers.update(HEADERS)

def _strip_prefix(v: str, prefix: str) -> str:
    v = (v or "").strip()
    if v.lower().startswith(prefix.lower()+":"):
        return v.split(":", 1)[1].strip()
    return v

def load_and_apply_headers_file(path: str):
    """Load a simple headers file that may contain lines like `Cookie: ...` and `User-Agent: ...`.
    Only these two headers are applied. Any accidental prefixes will be stripped.
    """
    try:
        ua, ck = None, None
        with open(path, 'r', encoding='utf-8') as f:
            for raw in f:
                line = raw.strip('\r\n').strip()
                if not line or ':' not in line:
                    continue
                k, v = line.split(':', 1)
                k = k.strip()
                v = v.strip()
                if k.lower() == 'user-agent':
                    ua = _strip_prefix(v, 'User-Agent')
                elif k.lower() == 'cookie':
                    ck = _strip_prefix(v, 'Cookie')
        if ua:
            SESSION.headers['User-Agent'] = ua
        if ck:
            SESSION.headers['Cookie'] = ck
        logging.info("已从 headers 文件应用 User-Agent 与 Cookie")
    except Exception as e:
        logging.warning(f"载入 headers 文件失败: {e}")

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

def daterange(start_date: datetime, end_date: datetime):
    d = start_date
    while d <= end_date:
        yield d
        d += timedelta(days=1)

def fetch_rank_page(date_str: str, brand_id: int, genre: int, page: int,
                    country: str = "cn", device: str = "iphone",
                    brand: str = "all", timeout=15, retries=3, backoff=1.6,
                    analysis: str | None = None) -> Dict[str, Any]:
    """
    请求单页数据。返回原始响应字典。
    说明：
      - 按你的观测，analysis 参数可省略，这里不传。
      - code==10000 代表成功；否则记 log 并返回字典（便于排错）。
      - 内置重试和限速处理。
    """
    url = BASE_URL.format(brand_id=brand_id)
    params = {
        "brand": brand,
        "country": country,
        "device": device,
        "date": date_str,
        "page": str(page),
        "genre": str(genre),
    }
    if analysis:
        params["analysis"] = analysis
    full_url = f"{url}?" + "&".join(f"{k}={v}" for k, v in params.items())
    print(f"[DEBUG] Fetching: {full_url}")
    last_err = None
    for attempt in range(retries):
        try:
            r = SESSION.get(url, params=params, timeout=timeout)
            if r.status_code == 429:
                time.sleep(backoff * (attempt + 1))
                continue
            r.raise_for_status()
            data = r.json()
            try:
                code = data.get("code")
                msg = data.get("msg") or data.get("message")
                logging.info(f"resp code={code} msg={msg} items={len(data.get('list', []) or [])}")
            except Exception:
                pass
            return data
        except Exception as e:
            last_err = e
            time.sleep(backoff * (attempt + 1))
    # 最后一次失败，返回带错误信息的字典
    return {"code": -1, "msg": f"request-failed: {last_err}", "status": getattr(last_err, 'response', None).status_code if hasattr(last_err, 'response') and last_err.response else None}

def ensure_dir(p: str):
    os.makedirs(p, exist_ok=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=str, help="起始日期 YYYY-MM-DD（含）",
                        default=(datetime.utcnow() - timedelta(days=365)).strftime("%Y-%m-%d"))
    parser.add_argument("--end", type=str, help="结束日期 YYYY-MM-DD（含）",
                        default=datetime.utcnow().strftime("%Y-%m-%d"))
    parser.add_argument("--genre", type=int, default=36, help="分类 genre ID（默认 36）")
    parser.add_argument("--brands", type=int, nargs="*", default=[0, 1, 2],
                        help="榜单类型 brand_id 列表：0付费/1免费/2畅销")
    parser.add_argument("--max_pages", type=int, default=10, help="每天每分类每榜单最多抓多少页（每页20条）")
    parser.add_argument("--out", type=str, default="qimai_out", help="输出目录")
    parser.add_argument("--sleep", type=float, default=0.5, help="请求间隔（秒）")
    parser.add_argument("--save-raw", action="store_true", help="保存原始响应 JSON")
    parser.add_argument("--save-flat", action="store_true", help="保存扁平 JSONL 记录")
    parser.add_argument("--cookie", type=str, default=None, help="直接传 Cookie 字符串（从浏览器复制）")
    parser.add_argument("--cookie_file", type=str, default=None, help="包含一行 Cookie 字符串的文件路径")
    parser.add_argument("--headers-file", type=str, default=None, help="仅包含 Cookie 与 User-Agent 的文件")
    args = parser.parse_args()
    args.max_pages = min(10, max(1, args.max_pages))  # 平台最多5页=Top200

    start = datetime.strptime(args.start, "%Y-%m-%d")
    end = datetime.strptime(args.end, "%Y-%m-%d")

    # 1) 先从文件加载（若提供），仅应用 UA & Cookie
    headers_file_used = False
    if getattr(args, 'cookie_file', None) and not args.cookie:
        try:
            with open(args.cookie_file, 'r', encoding='utf-8') as cf:
                args.cookie = cf.read().strip()
        except Exception as e:
            logging.warning(f"读取 cookie 文件失败: {e}")

    if getattr(args, 'headers_file', None):
        load_and_apply_headers_file(args.headers_file)
        headers_file_used = True

    # 2) 再用 --cookie 覆盖（若传入）
    if args.cookie:
        clean_cookie = _strip_prefix(args.cookie.replace('\n', ' ').replace('\r', ' '), 'Cookie')
        SESSION.headers['Cookie'] = clean_cookie
        logging.info("已注入自定义 Cookie（命令行优先）")

    # 3) 仅保留两项：User-Agent 与 Cookie（按你的要求）
    ua_final = SESSION.headers.get('User-Agent', HEADERS['User-Agent'])
    ck_final = SESSION.headers.get('Cookie', None)
    SESSION.headers.clear()
    SESSION.headers['User-Agent'] = ua_final
    if ck_final:
        SESSION.headers['Cookie'] = ck_final
    # logging.info(f"最终请求头(仅UA/Cookie): {SESSION.headers}")

    raw_root, flat_root, f_flat = None, None, None
    if args.save_raw:
        raw_root = os.path.join(args.out, "raw")
        ensure_dir(raw_root)
    if args.save_flat:
        flat_root = os.path.join(args.out, "flat")
        ensure_dir(flat_root)
        flat_path = os.path.join(flat_root, "records.jsonl")
        f_flat = open(flat_path, "a", encoding="utf-8")

    total_ok, total_pages, total_items = 0, 0, 0

    try:
        for d in daterange(start, end):
            date_str = d.strftime("%Y-%m-%d")
            for brand_id in args.brands:
                genre = args.genre  # 必传分类
                for page in range(1, args.max_pages + 1):
                    data = fetch_rank_page(date_str, brand_id, genre, page, analysis=None)
                    total_pages += 1

                    if args.save_raw and raw_root:
                        raw_dir = os.path.join(raw_root, date_str, f"brand_{brand_id}", f"genre_{args.genre}")
                        ensure_dir(raw_dir)
                        raw_file = os.path.join(raw_dir, f"page_{page}.json")
                        with open(raw_file, "w", encoding="utf-8") as fp:
                            json.dump(data, fp, ensure_ascii=False)

                    code = data.get("code")
                    if code != 10000:
                        logging.warning(f"非成功返回：code={code}, msg={data.get('msg')} (date={date_str}, brand={brand_id}, page={page})")
                        # code 非 10000 视为失败或空数据，直接跳出分页
                        # 常见：翻页超界、被限流、参数异常
                        # 也可以根据 msg 做更细的判断
                        break

                    lst: List[Dict[str, Any]] = data.get("list", []) or []
                    if not lst:
                        # 没有更多数据，结束此维度分页
                        break

                    if args.save_flat and f_flat:
                        for item in lst:
                            # 仅写debug扁平字段，真实写库走 service
                            app = item.get("appInfo", {}) or {}
                            klass = item.get("class", {}) or {}
                            rec = {
                                "dt": date_str,
                                "brand_id": brand_id,
                                "genre": args.genre,
                                "index": item.get("index"),
                                "rank": int(klass.get("ranking")) if klass.get("ranking") else None,
                                "change": item.get("change"),
                                "is_ad": item.get("is_ad"),
                                "appId": app.get("appId"),
                                "appName": app.get("appName"),
                                "publisher": app.get("publisher"),
                            }
                            f_flat.write(json.dumps(rec, ensure_ascii=False) + "\n")

                    upserted = upsert_page(date_str, brand_id, args.genre, lst)
                    total_items += upserted

                    total_ok += 1
                    time.sleep(args.sleep)

    finally:
        if f_flat:
            f_flat.close()

    print(f"Done. {total_ok} ok pages / {total_pages} total pages scanned / {total_items} items upserted")
    if flat_root:
        print(f"Flat JSONL: {os.path.join(flat_root, 'records.jsonl')}")
    if raw_root:
        print(f"Raw JSON:   {raw_root}")

if __name__ == "__main__":
    # 小心被限流；如遇 429/黑页，减小 --sleep 或手工加 cookie/代理
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted", file=sys.stderr)
        sys.exit(130)