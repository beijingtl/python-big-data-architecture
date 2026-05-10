df = spark.sql("select * from imdb_movies.ods_movies where imdb_title_id != 'imdb_title_id'")

# 1. 类型转换
from pyspark.sql.functions import col
new_df = df.withColumn("duration", col("duration").cast("int"))

import pyspark.sql.functions as F
df.withColumn("flag", F.lit(1))

# 2. 获取各列的基础统计信息
df_describe = new_df.describe()
df_describe[["summary", "title", "duration"]].show()

_ = new_df.agg({"duration": "min", "year": "max", "metascore":"avg" })
_.show()

# 3. 连接
right_df = spark.sql("select * from imdb_movies.ods_title_principals where imdb_title_id != 'imdb_title_id'")
left_df = new_df[["imdb_title_id"]].where("year = 1997")
_ = left_df.join(right_df, on="imdb_title_id", how="left")
_ = right_df.join(left_df, on="imdb_title_id", how="right")

_ = right_df.join(new_df.where("year = 1997"), on="imdb_title_id", how="left_semi")

_ = right_df.join(new_df.where("year = 1997"), on="imdb_title_id", how="left_anti")

left_df = new_df[["imdb_title_id"]].where("year = 1997")
_ = left_df.join(right_df.where("category = 'actor'"), on="imdb_title_id", how="inner")

# 4. 导出
new_df.write.csv('/user/hadoop/example/movies.csv', header=True)
new_df.write.parquet('/user/hadoop/example/movies.parquet')
new_df.write.orc('/user/hadoop/example/movies.orc')

# 导出到 Hive
new_df.registerTempTable("tmp_table_new_movies")
# spark.sql("insert into table imdb_movies.new_movies select * from tmp_table_new_movies")
new_df.write.format("hive").mode("overwrite").saveAsTable("imdb_movies.new_movies")