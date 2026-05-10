# -*- coding:utf-8 -*-

import pandas as pd
from pyspark.sql.functions import collect_set, size
from pyspark.ml.feature import OneHotEncoder, MinMaxScaler, VectorAssembler
from pyspark.ml.clustering import KMeans
from pyspark.ml.regression import RandomForestRegressor, RandomForestRegressionModel
from pyspark.ml.classification import LogisticRegression, LogisticRegressionModel
from pyspark.ml.evaluation import ClusteringEvaluator, RegressionEvaluator, BinaryClassificationEvaluator
from pyspark.ml.tuning import TrainValidationSplit, CrossValidator, ParamGridBuilder
from pyspark.ml.recommendation import ALS
from pyspark.ml.fpm import FPGrowth
from pyspark.ml import Pipeline, PipelineModel

# 12.5.1 准备数据
# 示例1、示例2、示例3的公用数据
# df_google = spark.createDataFrame(pd.read_csv('google_data.csv'))
df_google = spark.createDataFrame(pd.read_csv('第12章/google_data.csv'))
print(df_google.dtypes)
'''
[('Source', 'string'), ('WeekDay', 'bigint'), ('IsWeekEnd', 'bigint'), ('Users', 'bigint'), ('NewUsersRate', 'double'), ('BounceRate', 'double'), ('SessionDepth', 'double'), ('SessionDuration', 'double'), ('Revenue', 'double'), ('GoalComplete', 'bigint')]
'''

# 示例4和示例5的公用数据
# df_event = spark.createDataFrame(pd.read_csv('event_data.csv'))
df_event = spark.createDataFrame(pd.read_csv('第12章/event_data.csv'))
print(df_event.dtypes)
"""
[('UserID', 'bigint'), ('EventTime', 'string'), ('SKU', 'bigint')]
"""

# 12.5.2  特征工程和预处理
# 获得目标数据
num_features = ['IsWeekEnd', 'Users', 'NewUsersRate', 'BounceRate', 'SessionDepth', 'SessionDuration']
str_features = ['WeekDay']

# 哑编码转换
ohe_cols = ['ohe_' + i for i in str_features]
df1 = OneHotEncoder(inputCols=str_features, outputCols=ohe_cols, dropLast=False).fit(df_google).transform(df_google)
# df1 = OneHotEncoder(inputCol=str_features[0], outputCol='ohe_WeekDay', dropLast=False).transform(df_google) # 老版本用法，输入和输出都是单一字段
df1[['WeekDay', 'ohe_WeekDay']].limit(2).show(2)
'''
+-------+-------------+
|WeekDay|  ohe_WeekDay|
+-------+-------------+
|      5|(8,[5],[1.0])|
|      6|(8,[6],[1.0])|
+-------+-------------+
'''

# 将特征转换为向量格式
df2 = VectorAssembler(inputCols=num_features, outputCol='num_features').transform(df1)
# 数据归一化
df3 = MinMaxScaler(inputCol='num_features', outputCol='mm_features').fit(df2).transform(df2)
df3[['num_features', 'mm_features']].limit(2).show(2, truncate=False)
'''
+----------------------------------+----------------------------------------------------------------------------------------------------+
|num_features                      |mm_features                                                                                         |
+----------------------------------+----------------------------------------------------------------------------------------------------+
|[0.0,9126.0,0.79,0.31,4.4,145.1]  |[0.0,0.5188106796116505,0.411764705882353,0.4848484848484849,0.2637362637362638,0.29396654719235354]|
|[1.0,8726.0,0.94,0.35,5.47,170.05]|[1.0,0.4945388349514563,0.7058823529411763,0.6060606060606061,0.49890109890109885,0.443010752688172]|
+----------------------------------+----------------------------------------------------------------------------------------------------+
'''

# 所有向量组合为1个向量
df4 = VectorAssembler(inputCols=['ohe_WeekDay', 'mm_features'], outputCol='features').transform(df3)
df4[['features']].limit(2).show(2, truncate=False)
'''
+----------------------------------------------------------------+
|features                                                        |
+----------------------------------------------------------------+
|(14,[5,9,10,11,12,13],[1.0,0.030,0.176,0.303,1.0,0.736])        |
|(14,[6,8,9,10,11,12,13],[1.0,1.0,0.032,0.627,0.212,0.437,0.643])|
+----------------------------------------------------------------+
'''
df4[['ohe_WeekDay', 'mm_features', 'features']].limit(2).show(2, truncate=False)
'''
+-------------+------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------+
|ohe_WeekDay  |mm_features                                                                                           |features                                                                                                                           |
+-------------+------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------+
|(8,[5],[1.0])|[0.0,0.03046116504854369,0.17647058823529424,0.3030303030303031,1.0,0.7357825567502986]               |(14,[5,9,10,11,12,13],[1.0,0.03046116504854369,0.17647058823529424,0.3030303030303031,1.0,0.7357825567502986])                     |
|(8,[6],[1.0])|[1.0,0.03209951456310679,0.6274509803921569,0.21212121212121215,0.4373626373626374,0.6427120669056151]|(14,[6,8,9,10,11,12,13],[1.0,1.0,0.03209951456310679,0.6274509803921569,0.21212121212121215,0.4373626373626374,0.6427120669056151])|
+-------------+------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------+'''

# 12.5.3 核心算法应用
# 示例1: KMeans应用
df_kmeans = KMeans(featuresCol='features', predictionCol='kmeans_label', k=5).fit(df4).predict(df4)
# df_kmeans = KMeans(featuresCol='features', predictionCol='kmeans_label', k=5).fit(df4).transform(df4) # 老版本使用transform方法
df_kmeans[['features', 'kmeans_label']].limit(2).show(2, truncate=False)
'''
+------------------------------------------------------------------------------------------------------------------------------+------------+
|features                                                                                                                      |kmeans_label|
+------------------------------------------------------------------------------------------------------------------------------+------------+
|(14,[1,2,3,4,5,11],[0.5188106796116505,0.411764705882353,0.4848484848484849,0.2637362637362638,0.29396654719235354,1.0])      |1           |
|(14,[0,1,2,3,4,5,12],[1.0,0.4945388349514563,0.7058823529411763,0.6060606060606061,0.49890109890109885,0.443010752688172,1.0])|0           |
+------------------------------------------------------------------------------------------------------------------------------+------------+
'''
# kmeans模型评估
print(ClusteringEvaluator(featuresCol='features', predictionCol='kmeans_label').evaluate(df_kmeans))  # Silhouette
'''
0.6005131857334998
'''

# 示例2: RandomForest应用
df_rf = df4.withColumn('label', df4['Revenue'])
rf = RandomForestRegressor(featuresCol='features', labelCol='label')
grid = ParamGridBuilder().addGrid(rf.numTrees, [30]).build()
evaluator = RegressionEvaluator(metricName='r2')  # rmse/mae/mse/r2等
rf_cv_model = TrainValidationSplit(estimator=rf, estimatorParamMaps=grid, evaluator=evaluator, trainRatio=0.75).fit(
    df_rf)
print(rf_cv_model.validationMetrics[0])
'''
0.8450410399079773
'''

# 示例3: 逻辑回归应用
df_lr = df4.withColumn('label', df4['GoalComplete'])
lr = LogisticRegression()
grid = ParamGridBuilder().addGrid(lr.maxIter, [100]).build()
evaluator = BinaryClassificationEvaluator(metricName='areaUnderROC')  # areaUnderROC/areaUnderPR
lr_cv_model = TrainValidationSplit(estimator=lr, estimatorParamMaps=grid, evaluator=evaluator, trainRatio=0.75).fit(
    df_lr)
print(lr_cv_model.validationMetrics[0])
'''
0.9891928402566701
'''

# 示例4: ALS推荐应用
# 基于user、item的得分汇总
data_gb = df_event.groupby(['UserID', 'SKU']).agg({'EventTime': 'count'})
als = ALS(userCol='UserID', itemCol='SKU', ratingCol='count(EventTime)')
model = als.fit(data_gb)
# 针对用户的推荐
user_recs = model.recommendForAllUsers(3)
user_recs.limit(2).show(2, truncate=False)
'''
+------+----------------------------------------------------------+             
|UserID|recommendations                                           |
+------+----------------------------------------------------------+
|44052 |[[12087, 1.2474171], [12059, 1.206069], [12237, 1.109259]]|
|43923 |[[12241, 1.7065074], [12039, 1.128232], [12226, 1.1272]]  |
+------+----------------------------------------------------------+
'''
# 针对item的推荐
item_recs = model.recommendForAllItems(3)
item_recs.limit(2).show(2, truncate=False)
"""
+-----+------------------------------------------------------------+            
|SKU  |recommendations                                             |
+-----+------------------------------------------------------------+
|12046|[[43631, 3.1129465], [43730, 3.001854], [43772, 3.001854]]  |
|12139|[[43631, 2.5078537], [43915, 2.1063802], [43823, 1.8354053]]|
+-----+------------------------------------------------------------+
"""

# 示例5: FPGrowth频繁项集应用示例
df_event_gb = df_event.groupby(['UserID']).agg(collect_set('SKU'))  # 注意唯一集的集合
df_event_gb = df_event_gb.withColumn('pv', size(df_event_gb['collect_set(SKU)']))
df_event_filter = df_event_gb.filter(df_event_gb['pv'] >= 2)
df_event_filter.limit(3).show(3, truncate=False)
"""
+------+---------------------+---+
|UserID|collect_set(SKU)     |pv |
+------+---------------------+---+
|43684 |[12091, 12153]       |2  |
|43796 |[12109, 12155]       |2  |
|43525 |[12146, 12061, 12155]|3  |
+------+---------------------+---+
"""
# FPGrowth频繁项集和关联规则
fpm = FPGrowth(minSupport=0.01, minConfidence=0.01, itemsCol='collect_set(SKU)').fit(df_event_filter)
# TOP频繁项集
fpm.freqItemsets.limit(3).show(3, truncate=False)
"""
+--------------+----+
|items         |freq|
+--------------+----+
|[12050]       |40  |
|[12136]       |34  |
|[12136, 12084]|11  |
+--------------+----+
"""
# 关联规则
ass_rules = fpm.associationRules
rules_keep = ass_rules.select(ass_rules['antecedent'].alias('pattern_items'),
                              ass_rules['consequent'].alias('target_items'),
                              ass_rules['confidence'],
                              ass_rules['lift']
                              )
rules_keep.limit(3).show(3, truncate=False)
"""
+---------------------+------------+----------+-----------------+
|pattern_items        |target_items|confidence|lift             |
+---------------------+------------+----------+-----------------+
|[12036, 12040, 12136]|[12084]     |1.0       |9.176470588235293|
|[12036, 12040, 12136]|[12050]     |1.0       |7.800000000000001|
|[12036, 12040, 12136]|[12051]     |1.0       |26.0             |
+---------------------+------------+----------+-----------------+
"""

# 12.5.4 基于Pipelie管道式应用
# 指定字段
num_features = ['IsWeekEnd', 'Users', 'NewUsersRate', 'BounceRate', 'SessionDepth', 'SessionDuration']
str_features = ['WeekDay']
ohe_cols = ['ohe_' + i for i in str_features]
df_pipe = df_google.withColumn('label', df_google['GoalComplete'])

# 构建管道 TODO ohe新版本改为inputCols和outputCols
# pipe_ohe = [OneHotEncoder(inputCol=i, outputCol="ohe_" + i, dropLast=False) for i in str_features] # 老版本用法
ohe = OneHotEncoder(inputCols=str_features, outputCols=ohe_cols, dropLast=False)
va1 = VectorAssembler(inputCols=num_features, outputCol='num_features')
mm = MinMaxScaler(inputCol='num_features', outputCol='mm_features')
va2 = VectorAssembler(inputCols=["ohe_" + i for i in str_features] + ['mm_features'], outputCol='features')
lr = LogisticRegression()

# pipe_ohe = [OneHotEncoder(inputCol=i, dropLast=False) for i in str_features]
# ohe = OneHotEncoder(inputCols=str_features, outputCols=["ohe_" + i  for i in str_features], dropLast=False)
# va1 = VectorAssembler(inputCols=num_features)
# mm = MinMaxScaler(inputCol=va1.getOutputCol())
# va2 = VectorAssembler(inputCols=[i.getOutputCol() for i in pipe_ohe] + [mm.getOutputCol()], outputCol='features')

# stages = pipe_ohe + [va1, mm, va2, lr] # 老版本用法
stages = [ohe, va1, mm, va2, lr]
pipeline = Pipeline(stages=stages)

# fit过程+transform过程
pipeline_model = pipeline.fit(df_pipe)  # pipeline略耗时
df_pipe_result = pipeline_model.transform(df_pipe)  # pipeline略耗时
print(df_pipe_result.dtypes)
"""
[('Source', 'string'),
 ('WeekDay', 'bigint'),
 ('IsWeekEnd', 'bigint'),
 ('Users', 'bigint'),
 ('NewUsersRate', 'double'),
 ('BounceRate', 'double'),
 ('SessionDepth', 'double'),
 ('SessionDuration', 'double'),
 ('Revenue', 'double'),
 ('GoalComplete', 'bigint'),
 ('label', 'bigint'),
 ('ohe_WeekDay', 'vector'),
 ('num_features', 'vector'),
 ('mm_features', 'vector'),
 ('features', 'vector'),
 ('rawPrediction', 'vector'),
 ('probability', 'vector'),
 ('prediction', 'double')]
"""
# pipline的特征
df_pipe_result[['ohe_WeekDay', 'num_features', 'mm_features', 'features']].show(2, truncate=False)
"""
+-------------+----------------------------------+----------------------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------+
|(8,[5],[1.0])|[0.0,9126.0,0.79,0.31,4.4,145.1]  |[0.0,0.5188106796116505,0.411764705882353,0.4848484848484849,0.2637362637362638,0.29396654719235354]|(14,[5,9,10,11,12,13],[1.0,0.5188106796116505,0.411764705882353,0.4848484848484849,0.2637362637362638,0.29396654719235354])      |
|(8,[6],[1.0])|[1.0,8726.0,0.94,0.35,5.47,170.05]|[1.0,0.4945388349514563,0.7058823529411763,0.6060606060606061,0.49890109890109885,0.443010752688172]|(14,[6,8,9,10,11,12,13],[1.0,1.0,0.4945388349514563,0.7058823529411763,0.6060606060606061,0.49890109890109885,0.443010752688172])|
+-------------+----------------------------------+----------------------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------+
"""
# 原始分步骤的特征
df4[['ohe_WeekDay', 'num_features', 'mm_features', 'features']].show(2, truncate=False)
"""
+-------------+----------------------------------+----------------------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------+
|(8,[5],[1.0])|[0.0,9126.0,0.79,0.31,4.4,145.1]  |[0.0,0.5188106796116505,0.411764705882353,0.4848484848484849,0.2637362637362638,0.29396654719235354]|(14,[5,9,10,11,12,13],[1.0,0.5188106796116505,0.411764705882353,0.4848484848484849,0.2637362637362638,0.29396654719235354])      |
|(8,[6],[1.0])|[1.0,8726.0,0.94,0.35,5.47,170.05]|[1.0,0.4945388349514563,0.7058823529411763,0.6060606060606061,0.49890109890109885,0.443010752688172]|(14,[6,8,9,10,11,12,13],[1.0,1.0,0.4945388349514563,0.7058823529411763,0.6060606060606061,0.49890109890109885,0.443010752688172])|
+-------------+----------------------------------+----------------------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------+
"""
df_pipe_result[['rawPrediction', 'probability', 'prediction']].limit(2).show(2, truncate=False)
"""
+--------------------------------------+------------------------------------------+----------+
|rawPrediction                         |probability                               |prediction|
+--------------------------------------+------------------------------------------+----------+
|[8.02692253697283,-8.02692253697283]  |[0.9996735549864691,3.2644501353081945E-4]|0.0       |
|[6.235008990098221,-6.235008990098221]|[0.9980442209701221,0.001955779029877873] |0.0       |
+--------------------------------------+------------------------------------------+----------+
"""

# 获得特定过程对象
print(
    pipeline_model.stages)  # [OneHotEncoder_796c5713f5c7, VectorAssembler_2daf2eb7323a, MinMaxScaler_0cd09f9288d9, VectorAssembler_fa7e2a601884, LogisticRegressionModel: uid = LogisticRegression_b058533039cd, numClasses = 2, numFeatures = 14]
print(pipeline_model.stages[0])  # OneHotEncoder_796c5713f5c7
print(pipeline_model.stages[2].originalMax)  # DenseVector([1.0, 17056.0, 1.09, 0.48, 7.75, 263.29])
print(pipeline_model.stages[2].originalMin)  # DenseVector([0.0, 576.0, 0.58, 0.15, 3.2, 95.89])
print(dir(pipeline_model.stages[
              -1]))  # ['__class__', '__del__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__metaclass__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__slotnames__', '__str__', '__subclasshook__', '__weakref__', '_call_java', '_clear', '_copyValues', '_copy_params', '_create_from_java_class', '_create_params_from_java', '_defaultParamMap', '_dummy', '_empty_java_param_map', '_from_java', '_java_obj', '_make_java_param_pair', '_new_java_array', '_new_java_obj', '_paramMap', '_params', '_randomUID', '_resetUid', '_resolveParam', '_set', '_setDefault', '_shouldOwn', '_to_java', '_transfer_param_map_from_java', '_transfer_param_map_to_java', '_transfer_params_from_java', '_transfer_params_to_java', '_transform', 'aggregationDepth', 'coefficientMatrix', 'coefficients', 'copy', 'elasticNetParam', 'evaluate', 'explainParam', 'explainParams', 'extractParamMap', 'family', 'featuresCol', 'fitIntercept', 'getOrDefault', 'getParam', 'hasDefault', 'hasParam', 'hasSummary', 'intercept', 'interceptVector', 'isDefined', 'isSet', 'labelCol', 'load', 'lowerBoundsOnCoefficients', 'lowerBoundsOnIntercepts', 'maxIter', 'numClasses', 'numFeatures', 'params', 'predictionCol', 'probabilityCol', 'rawPredictionCol', 'read', 'regParam', 'save', 'set', 'standardization', 'summary', 'threshold', 'thresholds', 'tol', 'transform', 'uid', 'upperBoundsOnCoefficients', 'upperBoundsOnIntercepts', 'weightCol', 'write']

# 12.5.5 训练和预测拆分以及持久化操作
# 保存到HDFS
pipe_path = '/hdfs/models/pipe'
pipeline_model.write().overwrite().save(pipe_path)
pipeline_model_new = PipelineModel.load(pipe_path)

# 对比检验
print(pipeline_model.uid == pipeline_model_new.uid)
"""
True
"""
print(pipeline_model.stages, '\n', pipeline_model_new.stages)
"""
[OneHotEncoder_796c5713f5c7, VectorAssembler_2daf2eb7323a, MinMaxScaler_0cd09f9288d9, VectorAssembler_fa7e2a601884, LogisticRegressionModel: uid = LogisticRegression_b058533039cd, numClasses = 2, numFeatures = 14] 
[OneHotEncoder_796c5713f5c7, VectorAssembler_2daf2eb7323a, MinMaxScaler_0cd09f9288d9, VectorAssembler_fa7e2a601884, LogisticRegressionModel: uid = LogisticRegression_b058533039cd, numClasses = 2, numFeatures = 14]
"""

# 先完成训练
rfm = rf.fit(df_rf)

# 保存到HDFS
rfr_path = '/hdfs/models/rfm'
rfm.savewrite().overwrite().save(rfr_path)
rfm_new = RandomForestRegressionModel.load(rfr_path)

# 对比检验
print(rfm.uid == rfm_new.uid)
print(rfm.featureImportances, '\n', rfm_new.featureImportances)

# HDFS查看持久化的文件对象
# hdfs dfs -ls /hdfs/models/
"""
drwxr-xr-x   - hadoop hadoop          0 2022-01-11 09:36 /hdfs/models/pipe
drwxr-xr-x   - hadoop hadoop          0 2022-01-11 09:29 /hdfs/models/rfm
"""

# hdfs dfs -ls /hdfs/models/pipe
"""
drwxr-xr-x   - hadoop hadoop          0 2022-01-11 09:36 /hdfs/models/pipe/metadata
drwxr-xr-x   - hadoop hadoop          0 2022-01-11 09:36 /hdfs/models/pipe/stages
"""

# hdfs dfs -ls /hdfs/models/pipe/metadata
"""
-rw-r--r--   1 hadoop hadoop          0 2022-01-11 09:36 /hdfs/models/pipe/metadata/_SUCCESS
-rw-r--r--   1 hadoop hadoop        297 2022-01-11 09:36 /hdfs/models/pipe/metadata/part-00000
"""

# hdfs dfs -cat /hdfs/models/pipe/metadata/part-00000 | head -100
"""
{"class":"org.apache.spark.ml.PipelineModel","timestamp":1642073885531,"sparkVersion":"2.4.4","uid":"PipelineModel_10588bd07d5e","paramMap":{"stageUids":["OneHotEncoder_796c5713f5c7","VectorAssembler_2daf2eb7323a","MinMaxScaler_0cd09f9288d9","VectorAssembler_fa7e2a601884","LogisticRegression_b058533039cd"]},"defaultParamMap":{}}
"""

# hdfs dfs -ls /hdfs/models/pipe/stages
"""
drwxr-xr-x   - hadoop hadoop          0 2022-01-13 11:38 /hdfs/models/pipe/stages/0_OneHotEncoder_796c5713f5c7
drwxr-xr-x   - hadoop hadoop          0 2022-01-13 11:38 /hdfs/models/pipe/stages/1_VectorAssembler_2daf2eb7323a
drwxr-xr-x   - hadoop hadoop          0 2022-01-13 11:38 /hdfs/models/pipe/stages/2_MinMaxScaler_0cd09f9288d9
drwxr-xr-x   - hadoop hadoop          0 2022-01-13 11:38 /hdfs/models/pipe/stages/3_VectorAssembler_fa7e2a601884
drwxr-xr-x   - hadoop hadoop          0 2022-01-13 11:38 /hdfs/models/pipe/stages/4_LogisticRegression_b058533039cd
"""

# 模型同步到其他集群环境
# hadoop distcp -overwrite hdfs://source_master:8020/hdfs/models/pipe hdfs:target_master:8020/hdfs/models/pipe


# 12.5.6 自动调参的实现
paramGrid = ParamGridBuilder(). \
    addGrid(pipeline.stages[0].dropLast, [True, False]). \
    addGrid(pipeline.stages[-1].regParam, [0.0, 0.5]). \
    addGrid(pipeline.stages[-1].aggregationDepth, [2, 3]). \
    build()
evaluator = BinaryClassificationEvaluator(metricName='areaUnderROC')
pipe_grid_model = CrossValidator(estimator=pipeline, estimatorParamMaps=paramGrid, evaluator=evaluator,
                                 parallelism=4).fit(df_pipe)

# 基于自动调参的最佳模型检测结果
print(evaluator.evaluate(pipe_grid_model.transform(df_pipe)))
'''
0.9914381762790209
'''
