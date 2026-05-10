df = spark.sql("select * from imdb_movies.ods_movies where imdb_title_id != 'imdb_title_id'")

from pyspark.ml.feature import MinMaxScaler
from pyspark.ml.linalg import Vectors
from pyspark.sql.functions import col
df = spark.sql("select * from imdb_movies.ods_movies where imdb_title_id != 'imdb_title_id'")
df = df.withColumn("duration",col("duration").cast("int"))
mmScaler = MinMaxScaler(inputCol="duration", outputCol="scaled_duration")
model = mmScaler.fit(df)

# 1. 二值化
from pyspark.ml.feature import Binarizer
binarizer = Binarizer(threshold=90, inputCol="duration", outputCol="duration_bin")
binarizer_df = binarizer.transform(df.withColumn("duration",col("duration").cast("double")))
binarizer_df[["duration", "duration_bin"]].show(5)

# 2. 数据分桶
from pyspark.ml.feature import Bucketizer
bucketizer = Bucketizer(splits=[0,60,90,float("inf")], inputCol="duration", outputCol="duration_buck")
bucketizer_df = bucketizer.transform(df.withColumn("duration", col("duration").cast("double")))
bucketizer_df[["duration", "duration_buck"]].show(5)

# 3. 最小最大化、归一化
from pyspark.ml.feature import VectorAssembler, MinMaxScaler
vecAssembler = VectorAssembler(inputCols=["duration"], outputCol="duration_vec")
vecAssembler_df = vecAssembler.transform(df.withColumn("duration", col("duration").cast("double")))
vecAssembler = VectorAssembler(inputCols=["duration"], outputCol="duration_vec")
minMaxScaler = MinMaxScaler(min=0, max=1, inputCol="duration_vec", outputCol="duration_min_max_scaler")
minMaxScalerModel = minMaxScaler.fit(vecAssembler_df)
minMaxScaler_df = minMaxScalerModel.transform(vecAssembler_df)
minMaxScaler_df[["duration", "duration_vec", "duration_min_max_scaler"]].show(5)

# 4. 空值填充
fill_na_df = df.na.replace("", "other").fill("other")


# 5. 独热处理
from pyspark.ml.feature import OneHotEncoder, StringIndexer
fill_na_df = df.na.replace("", "other").na.fill("other")
stringIndexer = StringIndexer(inputCol="country", outputCol="country_indexed")
stringIndex_df = stringIndexer.fit(fill_na_df).transform(fill_na_df)
ohe = OneHotEncoder(inputCols=["country_indexed"], outputCols=["country_ohe"])
ohe_df = ohe.fit(stringIndex_df).transform(stringIndex_df)
ohe_df[["country", "country_indexed", "country_ohe"]].show(5)

# 6. PCA 降维
from pyspark.ml.feature import PCA
pca = PCA(k=20, inputCol="country_ohe", outputCol="country_pca")
pca_df = pca.fit(ohe_df).transform(ohe_df)
pca_df[["country", "country_ohe", "country_pca"]].show(5)