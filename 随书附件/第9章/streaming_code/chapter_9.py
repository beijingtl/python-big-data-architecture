# 定义数据源
def get_source(source_format='text'):
    if source_format in ['text', 'csv', 'json', 'orc', 'parquet']:
        return spark \
            .readStream \
            .format(source_format) \
            .option('path', f"/bigdata/test/pyspark/source/{source_format}/*") \
            .schema(StructType().add("value", "string")) \
            .load()
    # elif source_format == 'text':
    #     return spark \
    #         .readStream \
    #         .text("/bigdata/test/pyspark/source/text/*")
    # elif source_format in 'csv':
    #     return spark \
    #         .readStream \
    #         .csv("/bigdata/test/pyspark/source/csv/*", schema=StructType().add("value", "string"))
    # elif source_format == 'json':
    #     return spark \
    #         .readStream \
    #         .json("/bigdata/test/pyspark/source/json/*", schema=StructType().add("value", "string"))
    # elif source_format == 'orc':
    #     return spark \
    #         .readStream \
    #         .schema(StructType().add("value", "string")) \
    #         .option("mergeSchema", True) \
    #         .orc("/bigdata/test/pyspark/source/orc/*")
    # elif source_format == 'parquet':
    #     return spark \
    #         .readStream \
    #         .schema(StructType().add("value", "string")) \
    #         .option("mergeSchema", True) \
    #         .parquet("/bigdata/test/pyspark/source/parquet/*")
    elif source_format == 'socket':
        return spark \
            .readStream \
            .format("socket") \
            .option("host", "localhost") \
            .option("port", 9999) \
            .load()
    elif source_format == 'rate':
        return spark \
            .readStream \
            .format("rate") \
            .option("rowsPerSecond", "100") \
            .load()
    elif source_format == 'kafka':
        return spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", "localhost:32768,localhost:32769,localhost:32770") \
            .option("subscribe", "words1,words2") \
            .load()


# 将短语切分为词并统计字数
def streaming_process(lines, process_type='agg'):
    if process_type == 'agg':
        return lines.select(
            fn.explode(
                fn.split(lines.value, " ")
            ).alias("word")
        ).groupBy("word").count()
    elif process_type == 'map':
        return lines.selectExpr("CAST(value AS STRING)")
    elif process_type == 'select':
        return lines


# 启动应用并输出
def output_streaming(word_count, output_format='console'):
    if output_format in ['console', 'memory']:
        word_count \
            .writeStream \
            .queryName(f"{output_format}_sink") \
            .outputMode("complete") \
            .format(output_format) \
            .start().awaitTermination()
    elif output_format == 'kafka':
        word_count \
            .writeStream \
            .outputMode("update") \
            .format(output_format) \
            .option("kafka.bootstrap.servers", "localhost:32768,localhost:32769,localhost:32770") \
            .option("topic", "streaming_sink") \
            .trigger(continuous='0.1 second') \
            .start().awaitTermination()
    elif output_format in ['text', 'csv', 'json', 'orc', 'parquet']:
        if not os.path.exists(f'/bigdata/test/pyspark/output/{output_format}/'):
            os.makedirs(f'/bigdata/test/pyspark/output/{output_format}/')
        word_count \
            .writeStream \
            .outputMode("append") \
            .format(output_format) \
            .option("path", f"/bigdata/test/pyspark/output/{output_format}/") \
            .trigger(once=True) \
            .start().awaitTermination()
    elif output_format == 'foreach_batch':
        word_count \
            .writeStream \
            .outputMode("complete") \
            .foreachBatch(writer_RDBMS) \
            .trigger(processingTime='10 seconds') \
            .start().awaitTermination()


def main(source_format, process_type, output_format):
    lines = get_source(source_format)
    word_count = streaming_process(lines, process_type)
    output_streaming(word_count, output_format)


def writer_RDBMS(rows, epoch_id):
    rows.write.jdbc(
        'jdbc:mysql://192.168.0.54:3306/dwh?createDatabaseIfNotExist=TRUE&serverTimezone=UTC&useUnicode=true&characterEncoding=utf-8',
        'streaming_result',
        'overwrite',
        {'user': 'root', 'password': 'q1w2e3r4!'})


if __name__ == "__main__":
    # 导入环境库
    import os, sys, uuid
    from pyspark import SparkConf
    from pyspark.sql import SparkSession
    import pyspark.sql.functions as fn
    from pyspark.sql.types import StructType
    import redis

    # 配置环境信息
    conf = SparkConf() \
        .setAppName("structured_streaming_example") \
        .set('spark.sql.streaming.checkpointLocation', f'/bigdata/test/pyspark/checkpoint/{uuid.uuid1()}') \
        .set('ConfigurationOptions.ES_NODES', '127.0.0.1') \
        .set('ConfigurationOptions.ES_PORT', '9200')

    # 创建spark对象
    spark = SparkSession.builder. \
        config(conf=conf).getOrCreate()

    # 调用执行整个过程
    # print(spark.sparkContext.getConf().getAll())
    main(source_format=sys.argv[-3], process_type=sys.argv[-2], output_format=sys.argv[-1])
