import json, time
from elasticsearch import Elasticsearch

es = Elasticsearch(hosts="localhost:9200")

with open("./bq_ga_20170801.json", "r") as f:
    _all_data = f.readlines()

# 可以认为一行就是一个文档
test = json.loads(_all_str)
test = json.loads(_all_data[0])

# 尝试直接将一行数据插入文档
es.index("google-analytics-demo-20170801", test)
"""
{'_index': 'google-analytics-demo-20170801',
 '_type': '_doc',
 '_id': 'gV3mn3sBCtaYR5gNGL2j',
 '_version': 1,
 'result': 'created',
 '_shards': {'total': 2, 'successful': 1, 'failed': 0},
 '_seq_no': 0,
 '_primary_term': 1}
"""

# 查看该索引的详情
_index_detail = es.indices.get("google-analytics-demo-20170801")

# 循环插入
t1 = time.time()
for i in _all_data:
    i = json.loads(i)
    es.index("google-analytics-demo-20170801", i, id=f"{i['fullVisitorId']}-{i['visitId']}")
t2 = time.time()
print(f"【循环】文件索引花费时间：{t2-t1:.2f}s.")

# 清空 es 索引
es.indices.delete("google-analytics-demo-20170801")



import json, time
from elasticsearch import Elasticsearch

es = Elasticsearch(hosts="localhost:9200")

with open("./bq_ga_20170801.json", "r") as f:
    _all_data = f.readlines()

for i in _all_data:
    i = json.loads(i)
    es.index("google-analytics-demo-20170801", i, id=f"{i['fullVisitorId']}-{i['visitId']}")

# 插入检测
res = es.search(index="google-analytics-demo-20170801", 
    body={"query": {"match_all": {}}, },
    _source_includes=["fullVisitorId", "visitId", "totals"], 
    size=2)

es.get("google-analytics-demo-20170801", "2421708913980275160-1501651422", _source_includes=["fullVisitorId", "visitId", "totals"])

# 批量插入
def generate():
    for i in _all_data:
        i = json.loads(i)
        yield {
            "_index": "google-analytics-demo-20170801",
            "_id": f"{i['fullVisitorId']}-{i['visitId']}",
            "_source": i
        }

from elasticsearch import helpers
res = helpers.bulk(es, generate())

t1 = time.time()
res = helpers.bulk(es, generate())
t2 = time.time()
print(f"【批量】文件索引花费时间：{t2-t1:.2f}s.")

t1 = time.time()
# 异步多线程批量加载
res = helpers.parallel_bulk(es, generate())
t2 = time.time()
print(f"【并行批量】文件索引花费时间：{t2-t1:.2f}s.")