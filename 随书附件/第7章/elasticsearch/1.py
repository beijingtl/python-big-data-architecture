from elasticsearch import Elasticsearch

es = Elasticsearch(hosts="localhost:9200")
es.indices.create("es-test-index", {
    "mappings": {
        "properties": {
            "content": {
                "type": "text",
                "analyzer": "ik_max_word",
                "search_analyzer": "ik_smart"
            }
        }
    }
})

res = es.index("es-test-index", {"content": "Elasticsearch 是一个分布式的 RESTful 搜索和分析引擎。"})
es.index("es-test-index", {"content": "Elastic Stack 核心产品包括 Elasticsearch、Kibana、Beats 和 Logstash。"})
es.index("es-test-index", {"content": "Kibana 是一个免费且开放的用户界面，能够让您对 Elasticsearch 数据进行可视化。"})

es.index("es-test-index", {
    "content": "Kibana 是一个免费且开放的用户界面，能够让您对 Elasticsearch 数据进行可视化。",
    "title": "Kibana 简介"
    })

print(f"get result is: {es.get(res['_index'], res['_id'])}")

es.get(res['_index'], res['_id'], _source_includes="content" )


res = es.search(index="es-test-index", body={
  "query": {
    "match": {
      "content": "Elasticsearch 搜索"
    }
  }
})

res = es.search(index="es-test-index", body={
  "query": {
    "match": {
      "content": "Elasticsearch"
    }
  }
})

[ i["_score"] for i in res["hits"]["hits"]]



res = es.search(index="es-test-index", body={
  "query": {"match": {"content": "Elasticsearch"}}
})
print(f"search result is: {res}")





es.indices.analyze({
    "text": "Elasticsearch 是一个分布式、RESTful 风格的搜索和数据分析引擎。",
    # 如果不指定 field 则 analyzer 会使用默认的分析器
    "field": "content"
}, "es-test-index")


es.indices.analyze({
    "text": "我是中国人",
    "analyzer": "ik_max_word",
}, "es-test-index")

es.indices.analyze({
    "text": "我是中国人",
    "analyzer": "ik_smart"
}, "es-test-index")