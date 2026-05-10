#!/usr/bin/env python
# coding: utf-8


## 第一个简单示例
# 导入环境库
from pyspark import SparkConf
from pyspark.sql import SparkSession
import pyspark.sql.functions as fn

# 配置环境信息
conf = SparkConf(). \
    setAppName("structured_streaming_example1")
    
# 创建spark对象
spark = SparkSession.builder.\
    config(conf=conf).getOrCreate()
    
# 定义本地text文件数据源
#lines = spark\
#    .readStream \
#    .text("/bigdata/test/pyspark/sink/")
lines = spark\
    .readStream \
    .format('text') \
    .option("path","/bigdata/test/pyspark/sink/") \
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
