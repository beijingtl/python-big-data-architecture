#!/usr/bin/env python
# coding: utf-8


# 导入环境库
from pyspark import SparkConf
from pyspark.sql import SparkSession

# 配置环境信息
conf = SparkConf().setAppName("structured_streaming_example")

# 创建spark对象
spark = SparkSession.builder.config(conf=conf).getOrCreate()

# 定义本地text文件数据源
df = spark.readStream .text("/bigdata/test/pyspark/sink/new.log")

# 流计算过程--计算时间窗口内的PV量
pv_count = df.count()

# 执行程序
query = pv_count.writeStream.outputMode("append").format("console").start()
query.awaitTermination()