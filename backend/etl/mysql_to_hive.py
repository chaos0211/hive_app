# -*- coding: utf-8 -*-
"""
从 MySQL 读取 appstore_rankings_daily → 规则清洗 → 写入 Hive 分区表
分区：chart_date, brand_id, genre
写入模式：按分区覆盖（动态分区）
"""

import os
from pyspark.sql import SparkSession, functions as F, Window
from pyspark.sql.types import DecimalType, IntegerType, LongType, BooleanType, StringType, TimestampType

MYSQL_URL = "jdbc:mysql://127.0.0.1:33309/hive_app?useSSL=false&characterEncoding=utf8&serverTimezone=UTC"
MYSQL_USER = "root"
MYSQL_PWD  = "123456"
MYSQL_TABLE = "appstore_rankings_daily"

HIVE_DB = "hive_app"
HIVE_TABLE = "appstore_rankings_cleaned"

# 需要清洗的日期范围（可选参数化：用环境变量传入）
# 为空则全量；建议按天跑：EXPORT_START=2024-08-01 EXPORT_END=2024-08-31
EXPORT_START = os.environ.get("EXPORT_START")  # 'YYYY-MM-DD'
EXPORT_END   = os.environ.get("EXPORT_END")    # 'YYYY-MM-DD'

def build_spark():
    spark = (
        SparkSession.builder
        .appName("qimai-clean-to-hive")
        .enableHiveSupport()  # 🔑 使用 Hive Metastore
        # 覆盖分区需要
        .config("spark.sql.sources.partitionOverwriteMode", "dynamic")
        .config("spark.sql.hive.convertMetastoreParquet", "false")  # 避免某些环境分区识别问题
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")
    return spark

def read_mysql(spark):
    reader = (
        spark.read
        .format("jdbc")
        .option("url", MYSQL_URL)
        .option("user", MYSQL_USER)
        .option("password", MYSQL_PWD)
        .option("driver", "com.mysql.cj.jdbc.Driver")
        .option("dbtable", MYSQL_TABLE)
        # 拉大 fetchsize，减少往返
        .option("fetchsize", 2000)
    )
    df = reader.load()
    # 选取所需列（与模型一致）
    cols = [
        "chart_date","brand_id","country","device","genre","app_genre",
        "index","ranking","change","is_ad",
        "app_id","app_name","subtitle","icon_url","publisher","publisher_id","price",
        "file_size_bytes","file_size_mb","continuous_first_days",
        "source","raw_json","crawled_at","updated_at"
    ]
    df = df.select(*[c for c in cols if c in df.columns])
    return df

def apply_range_filter(df):
    if EXPORT_START and EXPORT_END:
        return df.filter((F.col("chart_date") >= EXPORT_START) & (F.col("chart_date") <= EXPORT_END))
    return df

def clean_rules(df):
    # 统一类型
    df = (
        df
        .withColumn("ranking", F.col("ranking").cast(IntegerType()))
        .withColumn("index", F.col("index").cast(IntegerType()))
        .withColumn("change", F.col("change").cast(IntegerType()))
        .withColumn("is_ad", F.col("is_ad").cast(BooleanType()))
        .withColumn("file_size_bytes", F.col("file_size_bytes").cast(LongType()))
        .withColumn("file_size_mb",
                    F.when(F.col("file_size_bytes").isNotNull(),
                           (F.col("file_size_bytes") / F.lit(1024*1024)).cast(DecimalType(18,2)))
                     .otherwise(None))
        .withColumn("price",
                    F.when(F.col("price").isNull(), F.lit(0.0)).otherwise(F.col("price")).cast(DecimalType(10,2)))
        .withColumn("app_name", F.trim(F.col("app_name").cast(StringType())))
        .withColumn("subtitle", F.trim(F.col("subtitle").cast(StringType())))
        .withColumn("publisher", F.trim(F.col("publisher").cast(StringType())))
        .withColumn("icon_url", F.trim(F.col("icon_url").cast(StringType())))
        .withColumn("app_genre", F.trim(F.col("app_genre").cast(StringType())))
        .withColumn("source", F.when(F.col("source").isNull(), F.lit("qimai")).otherwise(F.col("source")))
    )

    # 过滤无效/异常数据
    df = df.filter(F.col("app_id").isNotNull() & F.col("app_name").isNotNull())
    df = df.filter(F.col("ranking").between(1, 200))
    # 体积极端脏值过滤：> 40GB 视为异常（按需调整）
    df = df.filter((F.col("file_size_bytes").isNull()) | (F.col("file_size_bytes") <= F.lit(40*1024*1024*1024)))

    # 去重：同一分区键 + index 保留 updated_at 最新的一条
    w = Window.partitionBy("chart_date","brand_id","genre","country","device","index").orderBy(F.col("updated_at").desc_nulls_last())
    df = df.withColumn("_rn", F.row_number().over(w)).filter(F.col("_rn") == 1).drop("_rn")

    return df

def reorder_for_hive(df):
    # 按 Hive 表列顺序 & 分区列放最后
    cols = [
        "country","device","app_genre","index","ranking","change","is_ad",
        "app_id","app_name","subtitle","icon_url","publisher","publisher_id","price",
        "file_size_bytes","file_size_mb","continuous_first_days",
        "source","raw_json","crawled_at","updated_at",
        # partitions
        "chart_date","brand_id","genre"
    ]
    return df.select(*cols)

def write_to_hive(df):
    # 分区覆盖（只覆盖本次 DataFrame 中出现的分区）
    (
        df.write
        .mode("overwrite")
        .format("parquet")
        .partitionBy("chart_date","brand_id","genre")
        .saveAsTable(f"{HIVE_DB}.{HIVE_TABLE}")
    )

def main():
    spark = build_spark()
    try:
        df = read_mysql(spark)
        df = apply_range_filter(df)
        df = clean_rules(df)
        df = reorder_for_hive(df)
        write_to_hive(df)
        print(f"✅ Done. Wrote to {HIVE_DB}.{HIVE_TABLE}")
    finally:
        spark.stop()

if __name__ == "__main__":
    main()