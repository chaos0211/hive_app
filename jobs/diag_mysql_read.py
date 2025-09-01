from pyspark.sql import SparkSession, functions as F
import sys, json

spark = (SparkSession.builder
         .appName("diag_mysql")
         .config("hive.metastore.uris","thrift://localhost:9083")
         .getOrCreate())

url = "jdbc:mysql://127.0.0.1:33309/hive_app?useSSL=false&serverTimezone=UTC&allowPublicKeyRetrieval=true"

print("== JDBC URL ==", url, flush=True)

df = (spark.read.format("jdbc")
      .option("url", url)
      .option("user", "root")
      .option("password", "123456")
      .option("driver", "com.mysql.cj.jdbc.Driver")
      .option("dbtable", "appstore_rankings_daily")
      .load())

print("== schema ==", flush=True)
df.printSchema()

cnt = df.count()
print("== row count ==", cnt, flush=True)

print("== sample (20) ==", flush=True)
df.select("chart_date","brand_id","app_id","app_name","ranking") \
  .orderBy("chart_date","brand_id","ranking") \
  .show(20, truncate=False)

# 落地一小份到本地（非 Hive），方便肉眼确认
path = "/tmp/diag_mysql_sample.json"
df.limit(50).coalesce(1).write.mode("overwrite").json(path)
print(f"== wrote sample to {path}", flush=True)

spark.stop()