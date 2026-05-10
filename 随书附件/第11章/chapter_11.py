# -*- coding:utf-8 -*-

import jieba  # 单独安装 pip3 install jieba  -i https://mirrors.aliyun.com/pypi/simple/
import jieba.posseg as pseg
from jieba.analyse import extract_tags
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from prefixspan import PrefixSpan as pfs
from sklearn.cluster import KMeans  # 导入sklearn聚类模块
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_selection import VarianceThreshold
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, r2_score, explained_variance_score, mean_squared_error,silhouette_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier
from textrank4zh import TextRank4Sentence  # pip3 install textrank4zh

from 第11章 import apriori

#######################################################################################################


# 11.4 Python数据预处理技术
# 11.4.1 数据审核

df = pd.read_excel('第11章/data.xlsx')

# 打印预览数据
print(df.head(3))

# 查看数据类型、记录数、缺失值情况
print(df.info())

# 查看数据分布规律
print(round(df.describe()))
print(round(df.describe(include='all')))
print(df.describe(exclude=[np.number]))
print(df.describe(include=[object]))


# 11.4.2 缺失值处理
df['level'] = df['level'].fillna('others')  # 字符串类型缺失为others
df['age'] = df['age'].fillna(0)  # 用0填充
df['age'] = df['age'].fillna(df['age'].mean())  # 均值填充
df['age'] = df['age'].fillna(method='pad')  # 用前一个数据填充
df['age'] = df['age'].fillna(method='bfill')  # 用后一个数据填充
df['age'] = df['age'].interpolate(method='linear')  # 用差值法填充，可指定不同的方法

# 11.4.3 异常值处理
print(round(df[df['values'] != 1633742].describe()))

# 11.4.4 重复值处理
print(df[df.duplicated()])
print(df.drop_duplicates().shape)

# 11.4.5 抽样
print(df.sample(n=100).shape)  # 指定抽样数量为100
print(df.sample(frac=0.1).shape)  # 指定抽样比例为10%

# 11.4.6 数据标准化和归一化
ss_model = StandardScaler()  # 数据标准化
mm_model = MinMaxScaler((0, 1))  # 数据归一化
df['age_ss'] = ss_model.fit_transform(df[['age']])
df['age_mm'] = mm_model.fit_transform(df[['age']])
print(df[['age', 'age_ss', 'age_mm']].describe().T.round(2))

# 11.4.7 数据离散化和二元化
bins = [0, 2000, 100000, 200000, 500000, 1000000]
df['values_cut1'] = pd.cut(df['values'], bins)
df['values_cut2'] = pd.cut(df['values'], bins, labels=list('ABCDE'))
df['values_cut3'] = pd.cut(df['values'], 5, labels=list('ABCDE'))
print(df[['values', 'values_cut1', 'values_cut2', 'values_cut3']].head(3))

# 11.4.8 哑编码转换
print(df[['level']].head(3))
print(pd.get_dummies(df['level']).head(3))
enc = OneHotEncoder(handle_unknown='ignore', sparse=False)
enc.fit_transform(df[['level']])

# 11.4.9 特征共线性处理
print(np.round(df.corr(method='pearson'),2))

# 11.4.10 特征选择
df_num = df[['age', 'orders', 'values']]
model_vt = VarianceThreshold(threshold=0.1)
feature = model_vt.fit_transform(df_num)
print(model_vt.variances_)
print(df[['age', 'age_ss', 'age_mm']].describe().T[['std']].round(2))

# 11.4.11 降维
pca = PCA(n_components=2)
print(pca.fit_transform(df_num))
print(pca.explained_variance_ratio_)



#######################################################################################################


# 11.5 Python统计分析技术
# 统一导入库
raw_data = pd.read_excel('第11章/data2.xlsx')
print(raw_data.head(3))

# 11.5.1 对比分析
print(raw_data.groupby(['area_level'], as_index=False).agg({'order_value': 'max', 'uv': 'mean'}))

# 11.5.2 趋势分析
print(raw_data.groupby(['date'], as_index=False).agg({'order_value': 'mean', 'uv': 'mean'}))
#print(raw_data.groupby(['date'], as_index=False).agg({'order_value': 'mean', 'uv': 'mean'}).sort_values(['date'],ascending=True))

raw_data['month'] = raw_data['date'].map(lambda i: i.month)
print(raw_data.groupby(['month'], as_index=False).agg({'order_value': 'mean', 'uv': 'mean'}))

# 11.5.3 成分分析
com_data = raw_data.groupby(['area_level'], as_index=False)['order_value'].sum()
com_data['order_value_percent'] = com_data['order_value'] / com_data['order_value'].sum()
print(com_data.head())

# 11.5.4 数据透视表分析
print(raw_data.pivot_table(values=['order_value', 'uv'], index=['area_level'], columns=['is_campaign'], aggfunc=[np.mean]))
#print(raw_data.pivot_table(values=['order_value', 'uv'], index=['area_level'], columns=['is_campaign'], aggfunc=['sum', np.mean]))
#print(raw_data.pivot_table(values=['order_value', 'uv'], index=['month'],columns='is_campaign', aggfunc=['mean']))

# 11.5.5 相关性分析
print(raw_data[['order_value', 'uv']].corr(method='pearson').round(2))


#######################################################################################################


# 11.6 Python数据可视化技术
# 统一导入库
plt.rc("font",family="SimHei",size="14")  #用于解决中文显示乱码问题
plt.rcParams['axes.unicode_minus'] =False
raw_data = pd.read_excel('第11章/data2.xlsx')
com_data = raw_data.groupby(['area_level'], as_index=False)['order_value'].sum()

# 11.6.1 条形图
com_data.plot(kind='bar', x='area_level',y=['order_value'],
              figsize=(10, 4),title='各大区商品销售对比')
plt.show()

# 11.6.2 柱形图
com_data.plot(kind='barh', x='area_level',y=['order_value'],
              figsize=(10, 4),title='各大区商品销售对比')
plt.show()

# 11.6.3 折线图
date_data = raw_data.groupby(['date'], as_index=False).mean()
#date_data.plot(kind='line', x='date', y=['order_value', 'uv'], figsize=(10, 4), title='按月销售走势')
date_data.plot(kind='line', x='date', y=['order_value', 'uv'], secondary_y=['uv'],figsize=(10, 4), title='按月销售走势')
plt.show()

# 11.6.4 饼图
com_data.plot(kind='pie', y='order_value', figsize=(6, 6), title='各大区销售占比', autopct="%1.1f%%", labels=com_data['area_level'],legend=False)
plt.show()

# 11.6.5 散点图
raw_data.plot(kind='scatter',x='order_value', y='uv', figsize=(10, 4),title='order_value和uv关系')
plt.show()

# 11.6.6 成对关系图
sns.pairplot(raw_data[['order_value', 'uv', 'is_campaign']],kind='scatter',height=2,plot_kws=dict(s=80, edgecolor="white", linewidth=0.5))
plt.show()


# 11.6.7 热力图
cols = ['order_value', 'uv','is_campaign']
heatmap_data = raw_data[cols].corr(method='pearson')
sns.heatmap(heatmap_data, xticklabels=cols, yticklabels=cols, annot=True)
plt.show()

# 11.6.8 箱型图
plt.figure(figsize=(10,4))
sns.boxplot(x='area_level', y='order_value', data=raw_data)
plt.show()


#######################################################################################################


# 11.7 Python数据挖掘技术

# 11.7.1 聚类
# 读取数据
raw_data = pd.read_excel('第11章/data3.xlsx', sheet_name=0,index_col='user_id')
print(raw_data.head(3))
print(raw_data.info())

# 预处理
transformer = ColumnTransformer([("MinMaxScaler", MinMaxScaler(), [0,1,2]),
                                 ("OneHotEncoder", OneHotEncoder(), [3])])
train_features = transformer.fit_transform(raw_data)
print(train_features[:3,:])

# 聚类
model_kmeans = KMeans(n_clusters=3, random_state=0)  # 建立聚类模型对象
model_kmeans.fit(train_features)  # 训练聚类模型

# 模型评估
silhouette = silhouette_score(train_features, model_kmeans.labels_)
print(f'silhouette score: {silhouette}')

# 合并聚类结果
kmeans_labels = pd.DataFrame(model_kmeans.labels_,index=raw_data.index,columns=['labels'])
new_cols = ['age','orders','values']+list(transformer.transformers_[1][1].get_feature_names())
kmeans_features = pd.DataFrame(train_features,index=raw_data.index,columns=new_cols)
kmeans_data = pd.concat((kmeans_features,kmeans_labels),axis=1)
print(kmeans_data.head(3))

# 聚类结果分析
cluster_data = kmeans_data.groupby(['labels'],as_index=False).mean()
print(cluster_data)


# 11.7.2 关联

# 读取数据
raw_data = pd.read_excel('第11章/data3.xlsx',sheet_name=1)
print(raw_data.head(3))
print(raw_data.info())

# 预处理
data_drop = raw_data.dropna()
order_gb = data_drop.groupby('order_id')['sku'].unique().values.tolist()
order_list = [list(i) for i in order_gb if len(list(i)) > 1]

# 生成关联规则
L, suppData = apriori.apriori(order_list, minSupport=0.01)
rules = apriori.generateRules(order_list, L, suppData, minConf=0.05)

# 关联结果汇总
columns = ['sku1', 'sku2', 'instance', 'sup', 'conf','lift']
model_result = pd.DataFrame(rules, columns=columns)
print(model_result.head(3))


# 11.7.3 序列关联

# 读取数据
raw_data = pd.read_excel('第11章/data3.xlsx',sheet_name=2)
print(raw_data.head(3))
print(raw_data.info())

# 预处理
order_data = raw_data.sort_values(['cookie_id','event_time'])
print(order_data.tail(10))
order_records = order_data.groupby('cookie_id')['page'].unique().values.tolist()

# 序列关联
ps = pfs(order_records)
ps.maxlen = ps.minlen = 2
rec_sequences = ps.frequent(3)

# 结果解析
target_sequence_items = [[i[1][0], i[1][1], i[0]] for i in rec_sequences]
sequences = pd.DataFrame(target_sequence_items, columns=['page1', 'page2', 'sup'])
sequences_sort = sequences.sort_values(['sup'], ascending=False)
print(sequences_sort.head(3))


# 11.7.4 分类

# 读取数据
raw_data = pd.read_excel('第11章/data3.xlsx',sheet_name=3,index_col='user_id',comment='#',nrows=725)
x,y = raw_data.iloc[:,:-1],raw_data.iloc[:,-1]
print(raw_data.tail(3))
print(raw_data.info())

# 预处理
# 缺失值处理
x = x.fillna(x.mean())
print(x.info())
# 特征处理
transformer = ColumnTransformer([("OneHotEncoder", OneHotEncoder(), [0,1,2]),
                                 ("MinMaxScaler", MinMaxScaler(), [3,4]),])
train_features = transformer.fit_transform(x)
# 拆分训练集和测试集
x_train, x_test, y_train, y_test = train_test_split(train_features, y, test_size=.3, random_state=0)
#x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=.3, random_state=0)

# 模型训练
model_tree = DecisionTreeClassifier(max_depth=3,class_weight='balanced')
model_tree.fit(x_train, y_train)
pre_y = model_tree.predict(x_test)

# 模型评估
metrics = [accuracy_score,precision_score,recall_score,f1_score]
scores = [i(y_test, pre_y) for i in metrics]
columns = [i.__name__ for i in metrics]
scores_pd = pd.DataFrame(scores,index=columns).T
print(scores_pd)

# 预测新数据
new_data = pd.read_excel('第11章/data3.xlsx',sheet_name=3,index_col='user_id',comment='#',skiprows=728)
print(new_data.head(3))
print(new_data.info())
new_x = new_data.iloc[:,:-1]
new_features = transformer.transform(new_x)
new_data['order'] = model_tree.predict(new_features)
print(new_data)


# 11.7.5 回归

plt.rc("font",family="SimHei",size="14")  #用于解决中文显示乱码问题
plt.rcParams['axes.unicode_minus'] =False

# 读取数据
data = pd.read_excel('第11章/data3.xlsx',sheet_name=4,comment='#',nrows=1996)
print(data.tail(3))
print(data.info())

# 预处理
data_fill = data.dropna()
x,y = data_fill[['cost']],data_fill['uv']
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=.3, random_state=0)

# 分析关系
data_fill.plot(kind='scatter',x='cost',y='uv',figsize=(10,4),title='cost和uv的关系')
plt.show()

# 模型训练
rf = RandomForestRegressor(max_depth=2)
rf.fit(x_train, y_train)
pre_y = rf.predict(x_test)

# 模型评估
metrics = [r2_score,explained_variance_score,mean_squared_error]
scores = [i(y_test, pre_y) for i in metrics]
columns = [i.__name__ for i in metrics]
scores_pd = pd.DataFrame(scores,index=columns).T
print(scores_pd)

# 新数据预测
new_data = pd.read_excel('第11章/data3.xlsx',sheet_name=4,comment='#',skiprows=2000)
print(new_data.head(3))
print(new_data.info())
new_x = new_data[['cost']]
new_data['uv'] = rf.predict(new_x).round(0)
print(new_data.head(3))


#######################################################################################################


# 11.8.1 分词
with open('第11章/text.txt', encoding='utf8') as f:
    text_data = f.read()
print(text_data[:50])

cut_words = list(jieba.cut(text_data, cut_all=True, use_paddle=True))  # 精确模式分词
print(cut_words[:10])

# 11.8.2 文本清洗
# 基于词性的过滤
words = pseg.cut(text_data, use_paddle=True)  # paddle模式
keep_words1 = [word for word, flag in words if flag in ['v', 'n', 'nz']]
print(keep_words1[:10])
# 基于停用词的过滤
stop_words = ['产生', '到', '成为']
keep_words2 = [i for i in keep_words1 if i not in stop_words]
print(keep_words2[:10])

# 11.8.3 关键字提取
# 读取数据
with open('第11章/user_comment.txt',encoding='utf8') as fn:
    comment_data = fn.read()
print(comment_data[:50])
# 提取标签
print(extract_tags(comment_data, topK=50, withWeight=True, allowPOS=['a'])[:5])
print(extract_tags(comment_data, topK=50, withWeight=True, allowPOS=['n'])[:5])

# 11.8.4 自动摘要
# 读取数据
with open('第11章/articles.txt',encoding='utf8') as fn:
    text = fn.read()
# 摘要提取
tr4s = TextRank4Sentence()
tr4s.analyze(text=text)
for item in tr4s.get_key_sentences(num=3,sentence_min_len=6):
    print(item.index, item.weight, item.sentence)
