import happybase
conn = happybase.Connection(host='localhost', port=9090)
if not b"test" in conn.tables():
    conn.create_table("test", {"cf":dict()})

table = conn.table('test')
batch = table.batch()

for i in range(100,200):
    row_key = f"row{i}".encode("utf-8")
    data = {b"cf:test" : f"value{i}".encode("utf-8")}
    batch.put(row_key, data)

batch.send()