# -*- coding:utf-8 -*-

# 10.5 Python操作GraphFrames实现图计算


# 构建图对象
def build_graph():
    raw_data = spark.read.csv('/bigdata/test/pyspark/follow_data.csv', sep=',', header=True, inferSchema=True)
    v = raw_data[['id']].union(raw_data[['follow_id']]).drop_duplicates()  # vertices
    e = raw_data.selectExpr('id as src', 'follow_id as dst')  # edges，src/dst为固定名
    return GraphFrame(v, e)


def display(df, sort=False, sort_col=None, ascending=False):
    print(f'=========== DataFrame count: {df.count()} =========== ')
    df.show(3) if sort is False else df.orderBy(sort_col, ascending=ascending).show(3)


# 视图分析
def view_analysis(g):
    display(g.vertices)  # 顶点视图
    display(g.edges)  # 边视图
    display(g.triplets)  # 三元组视图


# 子顶点、子边和子图过滤
def sub_graph(g):
    display(g.dropIsolatedVertices().vertices)  # 去掉孤立点后的顶点数
    display(g.filterVertices('id <200 and id >5').vertices)  # 基于条件过滤的顶点
    display(g.filterEdges('src between 10 and 200 and dst <200').edges)  # 基于条件过滤的边视图
    display(g.filterVertices('id > 1000 ').filterEdges('dst = 2752').dropIsolatedVertices().triplets)


# 度分析
def degree_analysis(g):
    display(g.degrees, True, 'degree')  # 每个节点的度
    display(g.inDegrees, True, 'inDegree')  # 每个节点的入度
    display(g.outDegrees, True, 'outDegree')  # 每个节点的出度


# 模体查找
def motif_find(g):
    display(g.find('(node1)-[e]->(node2)'), True, 'node1')
    display(g.find('(node1)-[e1]->(node2); (node2)-[e2]->(node3)'), True, 'node1')
    display(g.find('(node1)-[e1]->(node2); (node2)-[e2]->(node3); (node3)-[e3]->(node4)'), True, 'node1')
    display(g.find('(node1)-[e1]->(node2); (node2)-[e2]->(node3); !(node1)-[]->(node3)'), True, 'node1')


# 持久化
def graphIO(g):
    # 保存
    g.vertices.write.parquet("pyspark/graph/vertices", mode='overwrite')
    g.edges.write.parquet("pyspark/graph/edges", mode='overwrite')

    # 加载
    same_v = spark.read.parquet("pyspark/graph/vertices")
    same_e = spark.read.parquet("pyspark/graph/edges")

    # 创建graph
    same_g = GraphFrame(same_v, same_e)


# 广度优先搜索
def bfs_search(g):
    display(g.bfs('id = 237', 'id = 2989', maxPathLength=1))  # 无法直接到达
    display(g.bfs('id = 237', 'id = 2989', maxPathLength=2))  # 存在3条路径（即通过第三方找到目标）


# 最短路径搜索
def shortest_search(g):
    result = g.shortestPaths(landmarks=['2752', '2782'])
    display(result)
    display(result.select(result.id.alias('source_id'), fn.explode('distances').alias('target_id', 'distance')))
    # g.bfs('id = 2400', 'id = 2752', maxPathLength=4))  # 打印最短路径


# 连通分量
def connected_components(g):
    spark.sparkContext.setCheckpointDir('checkpoint/cc')  # 必要条件
    display(g.connectedComponents(), True, 'component')  # 连通分量
    display(g.stronglyConnectedComponents(maxIter=8), True, 'component')  # 强连通分量


# 标签传播
def label_propagation(g):
    display(g.labelPropagation(maxIter=5), True, 'id')


# 网页排名
def page_rank(g):
    pr = g.pageRank(resetProbability=0.15, maxIter=10)
    display(pr.vertices, True, 'pagerank')  # PR值
    display(pr.edges, True, 'weight')  # 权重值


# 个性化网页排名
def personal_page_rank(g):
    pr2 = g.pageRank(resetProbability=0.15, sourceId='237', maxIter=10)
    display(pr2.vertices, True, 'pagerank')  # PR值
    display(pr2.edges, True, 'weight')  # 权重值


# 并行个性化网页排名
def parallel_personal_page_rank(g):
    pr3 = g.parallelPersonalizedPageRank(resetProbability=0.15, sourceIds=['237', '1201', '147'], maxIter=10)
    display(pr3.vertices, True, 'pageranks')  # PR值
    display(pr3.edges, True, 'weight')  # 权重值


# 三角形计数
def triangle_count(g):
    display(g.triangleCount(), True, 'count')  # 权重值


if __name__ == '__main__':
    from pyspark import SparkConf
    from pyspark.sql import SparkSession
    from pyspark.sql import functions as fn
    from graphframes import *

    # 初始化spark框架
    conf = SparkConf().setAppName("social_analysis")
    spark = SparkSession.builder.config(conf=conf).getOrCreate()

    # 构建图
    graph = build_graph()

    # 图计算
    view_analysis(graph)
    degree_analysis(graph)
    sub_graph(graph)
    degree_analysis(graph)
    motif_find(graph)
    graphIO(graph)
    bfs_search(graph)
    shortest_search(graph)
    connected_components(graph)
    label_propagation(graph)
    page_rank(graph)
    personal_page_rank(graph)
    parallel_personal_page_rank(graph)
