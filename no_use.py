from pyspark.sql import SparkSession

spark = (SparkSession.builder
    .appName("ods_app_ratings")
    .config("spark.sql.catalogImplementation", "hive")
    .getOrCreate())

# 假设df是DataFrame
df.write.mode("append") \
    .partitionBy("pt") \
    .format("parquet") \
    .save("/Users/chaos/data/lake/hive_app/ods_app_ratings")