import redis 

r = redis.Redis(host="host.docker.internal")
# 字符串操作
r.set("张三", 25)
print(f"张三的年龄：{r.getset('张三', 27).decode()}")
print(f"更新后张三的年龄：{r.get('张三').decode()}")
r.delete("张三") 

# 散列操作
r = redis.Redis(host="host.docker.internal", decode_responses=True)
r.hset("张三", mapping={"年龄":27, "性别":"男"})
print(f"张三的年龄：{r.hget('张三', '年龄')}")
print(f"张三的基本信息：{r.hmget('张三', '年龄', '性别')}")
r.hdel("张三", "性别")

# 列表操作
r.rpush("工作日", "周三", "周四")
r.lpush("工作日", "周二", "周一")
r.linsert("工作日", "after", "周四", "周五")
print(f"工作日：{r.lrange('工作日', 0, 7)}")
print(f"工作日的第一天：{r.blpop('工作日')}")
print(f"工作日的最后一天：{r.brpop('工作日')}")
r.ltrim("工作日", 1, 0)

# 集合操作
r.sadd("redis:data-types", "binary-safe-strings", "hashes", "lists", "sets", "sort-sets", "bit-arrays", "hyperloglogs", "streams")
print(f"hashes 是 redis 中的数据类型：{r.sismember('redis:data-types', 'hashes')}")
print(f"redis 中的数据类型：{r.smembers('redis:data-types')}")
r.srem("redis:data-types", "bit-arrays", "hyperloglogs", "streams") 
print(f"剩余redis数据类型个数：{r.scard('redis:data-types')}")

# 有序集合操作
r.zadd("考试成绩", {"张三":100, "李四":80, "王五":55})
print(f"各同学考试成绩为：{r.zrange('考试成绩', 0, -1, withscores=True)}")
print(f"王五同学的排名是：{r.zrevrank('考试成绩', '王五') + 1}")
print(f"张三同学的得分是{r.zscore('考试成绩', '张三')}")
r.zrem("考试成绩", "王五", "张三", "李四")