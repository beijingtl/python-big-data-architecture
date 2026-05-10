from elasticsearch import Elasticsearch

es = Elasticsearch(hosts="host.docker.internal:9200")

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
print(f"res is： {res}")
es.index("es-test-index", {"content": "Elasticsearch 是一个分布式的 RESTful 搜索和分析引擎。"})
es.index("es-test-index", {"content": "Elasticsearch 是一个分布式的 RESTful 搜索和分析引擎。"})

print(f"get result is: {es.get(res['_index'], res['_id'])}")

es.search

bulk_doc = '''
{ "index" : { "_index" : "test", "_id" : "1" } }
{ "field1" : "value1" }
{ "delete" : { "_index" : "test", "_id" : "2" } }
{ "create" : { "_index" : "test", "_id" : "3" } }
{ "field1" : "value3" }
{ "update" : {"_id" : "1", "_index" : "test"} }
{ "doc" : {"field2" : "value2"} }
'''
es.bulk(bulk_doc)

