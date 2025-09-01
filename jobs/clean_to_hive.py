#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from datetime import datetime, timedelta

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import BooleanType, IntegerType, LongType, DoubleType, StringType, TimestampType, DateType

def parse_args():
    p = argparse.ArgumentParser(description="MySQL → Spark 清洗 → Hive 分区表")
    p.add_argument("--mysql-url", required=True, help="JDBC，如 jdbc:mysql://127.0.0.1:33309/hive_app?useSSL=false&serverTimezone=UTC")
    p.add_argument("--mysql-user", required=True)
    p.add_argument("--mysql-password", required=True)
    p.add_argument("--mysql-table", default="appstore_rankings_daily", help="MySQL 表名，默认 ranking")

    p.add_argument("--start", help="开始日期 YYYY-MM-DD（含），若未指定 --all 则必填")
    p.add_argument("--end", help="结束日期 YYYY-MM-DD（含），若未指定 --all 则必填")
    p.add_argument("--brands", nargs="+", type=int, default=[0,1,2], help="brand_id 列表，例：0 1 2")
    p.add_argument("--genre-id", type=int, default=36, help="genre 分区值（你的爬虫默认 36）")
    p.add_argument("--all", action="store_true", help="忽略 --start/--end/--brands 过滤，导入 MySQL 全量数据")

    p.add_argument("--hive-db", default="hive_app")
    p.add_argument("--hive-table", default="ranking_clean")

    return p.parse_args()

def daterange(start_date, end_date):
    d0 = datetime.strptime(start_date, "%Y-%m-%d").date()
    d1 = datetime.strptime(end_date, "%Y-%m-%d").date()
    delta = (d1 - d0).days
    for i in range(delta + 1):
        yield d0 + timedelta(days=i)

def main():
    args = parse_args()

    # 参数校验：未开启 --all 时必须提供 --start/--end
    if not args.all:
        if not args.start or not args.end:
            raise SystemExit("错误：未指定 --all 时，--start 与 --end 为必填参数（格式 YYYY-MM-DD）。")

    spark = (
        SparkSession.builder
        .appName("mysql_to_hive_clean")
        # 让 overwrite 只覆盖目标分区（非常关键）
        .config("spark.sql.sources.partitionOverwriteMode", "dynamic")
        .config("spark.sql.parquet.compression.codec", "snappy")
        # 连接 Hive Metastore
        .config("hive.metastore.uris", "thrift://localhost:9083")
        .enableHiveSupport()
        .getOrCreate()
    )

    # 读取 MySQL（仅针对目标日期 & 品牌）
    # 假设 MySQL ranking 表列包含：chart_date, brand_id, 以及你模型里定义的字段
    jdbc_kwargs = {
        "url": args.mysql-url if False else args.mysql_url,  # 保留一行防 IDE 误报
        "user": args.mysql_user,
        "password": args.mysql_password,
        "driver": "com.mysql.cj.jdbc.Driver",
        "dbtable": args.mysql_table,
        "fetchsize": "1000",
    }

    df_mysql = spark.read.format("jdbc").options(**jdbc_kwargs).load()

    # 过滤日期 & 品牌（支持 --all 全量导入；健壮匹配列名）
    if args.all:
        df_filt = df_mysql
    else:
        dates = [str(d) for d in daterange(args.start, args.end)]
        cand_date_cols = [c for c in df_mysql.columns if c.lower() in ("chart_date","date")]
        date_col = cand_date_cols[0] if cand_date_cols else "chart_date"
        cand_brand_cols = [c for c in df_mysql.columns if c.lower() in ("brand_id","brand")]
        brand_col = cand_brand_cols[0] if cand_brand_cols else "brand_id"
        df_filt = (
            df_mysql
            .where(F.col(date_col).isin(dates))  # 不做 cast，兼容 VARCHAR 日期
            .where(F.col(brand_col).cast(IntegerType()).isin(args.brands))
        )
    print("rows after filter =", df_filt.count(), flush=True)

    # 若源表已有 genre_id/genreId 列则优先使用，否则用命令行参数
    cand_gid_cols = [c for c in df_filt.columns if c.lower() in ("genre_id","genreid")]
    genre_id_expr = F.col(cand_gid_cols[0]).cast(IntegerType()) if cand_gid_cols else F.lit(args.genre_id).cast(IntegerType())

    # 字段标准化/重命名 → 对齐 Hive 表 schema
    # 你的后端模型里已是统一命名，这里再兜底转换一次
    df_clean = (
        df_filt
        .withColumn("index", F.col("index").cast(IntegerType()))
        .withColumn("app_id", F.col("app_id").cast(StringType()))
        .withColumn("app_name", F.col("app_name").cast(StringType()))
        .withColumn("subtitle", F.col("subtitle").cast(StringType()))
        .withColumn("icon_url", F.col("icon_url").cast(StringType()))
        .withColumn("publisher", F.col("publisher").cast(StringType()))
        .withColumn("country", F.col("country").cast(StringType()))
        .withColumn("file_size_bytes", F.col("file_size_bytes").cast(LongType()))
        .withColumn("file_size_mb", (F.col("file_size_bytes") / F.lit(1048576.0)).cast(DoubleType()))
        .withColumn("price", F.col("price").cast(DoubleType()))
        .withColumn("ranking", F.col("ranking").cast(IntegerType()))
        .withColumn("change", F.col("change").cast(StringType()))
        .withColumn("genre", F.col("genre").cast(StringType()))
        .withColumn("app_genre", F.col("app_genre").cast(StringType()))
        .withColumn("publisher_id", F.col("publisher_id").cast(StringType()))
        .withColumn("is_ad", F.col("is_ad").cast(BooleanType()))
        .withColumn("continuous_first_days", F.col("continuous_first_days").cast(IntegerType()))
        .withColumn("crawled_at", F.col("crawled_at").cast(TimestampType()))
        .withColumn("updated_at", F.col("updated_at").cast(TimestampType()))
        .withColumn("source", F.coalesce(F.col("source"), F.lit("mysql")))
        .withColumn("chart_date", F.col("chart_date").cast(DateType()))
        .withColumn("brand_id", F.col("brand_id").cast(IntegerType()))
        .withColumn("genre_id", genre_id_expr)
        # 只保留 Hive 表需要的列
        .select(
            "index","app_id","app_name","subtitle","icon_url","publisher","country",
            "file_size_bytes","file_size_mb","price","ranking","change","genre","app_genre",
            "publisher_id","is_ad","continuous_first_days","crawled_at","updated_at","source",
            "chart_date","brand_id","genre_id"
        )
    )

    # 动态覆盖写入目标分区（chart_date, brand_id, genre_id）
    target = f"{args.hive_db}.{args.hive_table}"
    (
        df_clean
        .repartition("chart_date","brand_id","genre_id")
        .write
        .mode("overwrite")
        .format("parquet")
        .partitionBy("chart_date","brand_id","genre_id")
        .saveAsTable(target)
    )

    # 可选：产出每日 KPI（写入 ranking_daily_agg）
    df_day = df_clean.groupBy("chart_date","brand_id","genre_id").agg(
        F.count(F.lit(1)).alias("total_apps"),
        F.avg(F.when(F.col("is_ad") == True, F.lit(1.0)).otherwise(F.lit(0.0))).alias("ad_ratio"),
        F.collect_list(F.struct(F.col("publisher").alias("publisher"))).alias("pubs"),
        F.current_timestamp().alias("updated_at")
    )

    # 粗略统计前10 publisher（按出现次数）
    df_top10 = (
        df_clean.groupBy("chart_date","brand_id","genre_id","publisher")
        .agg(F.count(F.lit(1)).alias("cnt"))
        .withColumn("kv", F.struct(F.col("publisher"), F.col("cnt")))
        .groupBy("chart_date","brand_id","genre_id")
        .agg(F.slice(F.sort_array(F.collect_list("kv"), asc=False), 1, 10).alias("top10_publishers"))
    )

    df_kpi = (
        df_day
        .join(df_top10, ["chart_date","brand_id","genre_id"], "left")
        .select("chart_date","brand_id","genre_id","total_apps","ad_ratio","top10_publishers","updated_at")
    )

    (
        df_kpi
        .repartition("chart_date","brand_id","genre_id")
        .write
        .mode("overwrite")
        .format("parquet")
        .partitionBy("chart_date","brand_id","genre_id")
        .saveAsTable(f"{args.hive_db}.ranking_daily_agg")
    )

    spark.sql(f"MSCK REPAIR TABLE {args.hive_db}.{args.hive_table}")
    spark.sql(f"MSCK REPAIR TABLE {args.hive_db}.ranking_daily_agg")
    spark.stop()

if __name__ == "__main__":
    main()