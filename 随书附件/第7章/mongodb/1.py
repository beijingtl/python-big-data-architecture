import pymongo

with pymongo.MongoClient(host='172.17.0.2', port=27017) as client:
    db = client["example"]
    collection = db["user"]
    collection.insert_one({"name": "张三", "year": 27, "gender": "男"})
    collection.insert_many([
        {"name": "李四", "year": 26, "gender": "女"},
        {"name": "王五", "gender": "女", "hobby": ["跑步", "读书"]},
    ])
    print(collection.find_one({ "$or": [{"year": {"$gt": 28}}, {"gender": {"$eq": "女"}}]}))
    collection.update_one({'name': "王五"}, {'$set': {'year': 24}, "$set": {'gender': "男"}})
    collection.update_many({}, {"$set": {"job": "Data Engineer"}})
    for i in collection.find({}, projection={"name":1, "_id":0}):print(i)
    collection.delete_one({"name": "李四"})
    delete_result = collection.delete_many({})
    print(f"删除文档数：{delete_result.deleted_count}")
    print(f"集合中现存文档数：{collection.count_documents({})}")

client.server_info()
client.list_database_names()