import pymongo, json

with pymongo.MongoClient(host='172.17.0.2', port=27017) as client:
    db = client["example"]
    collection = db["ga_demo"]

    with open("./bq_ga_20170801.json", "r") as f:
        _all_data = f.readlines()
        _all_data = [json.loads(i) for i in _all_data]

    collection.insert_many(_all_data)
    print(f"集合中现存文档数：{collection.count_documents({})}")


with pymongo.MongoClient(host='172.17.0.2', port=27017) as client:
    db = client["example"]
    collection = db["ga_demo"]

    res = collection.aggregate([
        {"$group": { "_id": "$device.browser", "total": {"$sum": 1}}},
    ])
    for i in res: print(i)

    res = collection.aggregate([
        {"$match": { "visitNumber" : {"$eq": "1"}}},
        {"$group": { "_id": "$device.browser", "total": {"$sum": 1}}},
    ])
    for i in res: print(i)

    res = collection.aggregate([
        {"$match": { "visitNumber" : {"$eq": "1"}}},
        {"$group": { "_id": "$device.browser", "total": {"$sum": 1}}},
        {"$sort": { "total": -1}},
    ])
    for i in res: print(i)

    res = collection.aggregate([
        {"$match": { "visitNumber" : {"$eq": "1"}}},
        {"$group": { "_id": "$device.browser", "total": {"$sum": 1}}},
        {"$sort": { "total": -1}},
        {"$out": { "db": "example", "coll": "new_visit_browser_dist" } }
    ])
    print(db["new_visit_browser_dist"].find_one())
    print(db["new_visit_browser_dist"].count_documents({}))

    res = collection.aggregate([
        {"$group": { "_id": None, "total": {"$sum": "$visitNumber"}}},
    ])
    for i in res: print(i)

result = db.things.insert_many([{"x": 1, "tags": ["dog", "cat"]},
                           {"x": 2, "tags": ["cat"]},
                            {"x": 2, "tags": ["mouse", "cat", "dog"]},
                             {"x": 3, "tags": []}])
db.things.aggregate([
    {"$unwind": "$tags"},
])


