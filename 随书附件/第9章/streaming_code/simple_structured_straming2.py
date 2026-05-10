#!/usr/bin/env python
# coding: utf-8


## 第二个简单示例
# 导入环境库
from pyspark import SparkConf
from pyspark.sql import SparkSession
import pyspark.sql.functions as fn


# 配置环境信息
conf = SparkConf().setAppName("structured_streaming_example2")

# 创建spark对象
spark = SparkSession.builder.\
    config(conf=conf).getOrCreate()
	
# 定义数据源，指定为从本地（localhost）9999端口获得数据
lines = spark \
    .readStream \
    .format("socket") \
    .option("host", "localhost") \
    .option("port", 9999) \
    .load()

# 将短语切分为词并统计字数
word_count = lines.select(
   fn.explode(
       fn.split(lines.value, " ")
   ).alias("word")
).groupBy("word").count()

# 启动应用并在终端打印输出
query = word_count \
    .writeStream \
    .outputMode("complete") \
    .format("console") \
    .start()

query.awaitTermination()


# 启动
spark-submit /bigdata/test/pyspark/streaming_code/simple_structured_straming2.py