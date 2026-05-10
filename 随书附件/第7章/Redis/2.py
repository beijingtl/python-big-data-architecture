import redis 

r = redis.Redis(host="host.docker.internal", decode_responses=True, db=1)

for i in range(0, 100000):
    _ = f"150659863.{str(int(1627114553)+i)}"
    r.sadd("cid", _)
    if (i+1) % 10000 == 0:
        print(f"[{i+1}] cid length: {r.scard('cid')}, memory useage: {r.memory_usage('cid')}")

# HyperLogLog 操作
r.delete("cid")

for i in range(0, 100000):
    _ = f"150659863.{str(int(1627114553)+i)}"
    r.pfadd("cid", _)
    if (i+1) % 10000 == 0:
        print(f"[{i+1}] cid length: {r.pfcount('cid')}, memory useage: {r.memory_usage('cid')}")