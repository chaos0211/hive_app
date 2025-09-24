from pyspark.sql import SparkSession
from pyspark.sql import functions as F

DAY = "2025-09-12"   # 改成你要跑的分区

spark = (SparkSession.builder
         .appName("ods->dwd_rankings_c")
         .config("spark.sql.parquet.compression.codec", "snappy")
         .getOrCreate())

# 1) 读 ODS（你的 ods_app_ratings Parquet 根目录）
ods_root = "/Users/chaos/data/lake/hive_app/ods_app_ratings"
df = spark.read.parquet(ods_root).filter(F.col("pt") == DAY)

# 2) 只保留 rank_c 正常 JSON 的记录
df = df.filter((F.col("rank_c").isNotNull()) & (F.col("rank_c") != ""))

from pyspark.sql.column import Column  # add import (safe if unused elsewhere)

# 3) 提取 JSON 字段
#   注意：get_json_object 返回 STRING，这里强转 ranking/change 为 INT，失败给 null
def to_int_safe(c: Column):
    """Safely cast a STRING Column to INT when it matches digits; else return NULL."""
    return F.when(c.rlike("^[0-9]+$"), c.cast("int")).otherwise(F.lit(None).cast("int"))

r_genre   = F.get_json_object(F.col("rank_c"), "$.genre").alias("genre")
r_ranking = to_int_safe(F.get_json_object(F.col("rank_c"), "$.ranking")).alias("ranking")
r_change  = to_int_safe(F.get_json_object(F.col("rank_c"), "$.change")).alias("change")

# 4) 选择 DWD 所需列（rating 这里先不做强转，保持为 NULL，避免 Hive CASE/CAST 触发 MR 异常）
dwd = (df.select(
        "app_id", "app_name", "publisher",
        r_genre, r_ranking, r_change,
        F.lit(None).cast("double").alias("rating"),
        "rating_num", "is_ad", "icon_url",
        "pt", "country", "device", "brand"
      )
      .withColumn("rank_scope", F.lit("c"))
     )

# 5) 写到 DWD 目录（与 Hive 表 dwd_app_rankings 的 LOCATION 对齐）
#    注意 partitionBy 顺序必须与 Hive 表的 partition keys 一致
dwd_root = "/Users/chaos/data/lake/hive_app/dwd_app_rankings"   # 你之前 DWD 表的 LOCATION
(dwd.write
    .mode("overwrite")   # 数据稳定后改成append
    .partitionBy("pt", "country", "device", "brand", "rank_scope")
    .parquet(dwd_root))

spark.stop()
print("DONE")