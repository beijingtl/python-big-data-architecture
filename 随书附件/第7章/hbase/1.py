import happybase
conn = happybase.Connection(host='localhost', port=9090)
if not b"test" in conn.tables(): 
    conn.create_table("test", {"cf":dict()})

table = conn.table('test')
table.put(b'row1', {b'cf:a': b'value1'})
table.put(b'row2', {b'cf:b': b'value2'})
table.put(b'row3', {b'cf:c': b'value3'})
table.put(b'row4', {b'cf:d': b'value4'})

row = table.row(b'row1')
# row = table.row(b'row1', ["cf:a", "cf:b"], include_timestamp=True)
# row = table.row(b'row1', timestamp=2**16, include_timestamp=True)
print(row) 

for key, data in table.rows([b'row3', b'row1']):
    print(key, data)

# table.scan("row1", "row3")

for key, data in table.scan(row_prefix=b'row'):
    print(key, data)

# 数据更新
table.put(b'row1', {b'cf:a': b'value1_version4'}, timestamp=9633597970133)
# table.put(b'row1', {b'cf:b': b'version_1'})

table.cells(b"row1", b"cf:a", include_timestamp=True)

# table.delete(b'row1')

# conn.close()
table.put(b'row_e_1', {b'cf:name': b'zhangsan'})
table.put(b'row_e_3', {b'cf:sex': b'male'})
table.put(b'row_e_3', {b'cf:abc': b'test'})
table.put(b'row_e_2', {b'cf:name': b'lisi'})
table.put(b'row_e_3', {b'cf:name': b'wangwu'})


for key, data in table.scan(filter=b"SingleColumnValueFilter ('cf', 'name', =, 'binary:ang')"):
    print(key, data)

# KeyOnlyFilter 不做过滤，仅返回 key
for key, data in table.scan(filter=b"KeyOnlyFilter ()"):
    print(key, data)

# 仅返回一个key 这块key的返回顺序也是基于字典的
for key, data in table.scan(filter=b"FirstKeyOnlyFilter ()"):
    print(key, data)

for key, data in table.scan(filter=b"ColumnPrefixFilter ('a')"):
    print(key, data)



import happybase
conn = happybase.Connection(host='localhost', port=9090)
if not b"test" in conn.tables(): # enable 只是一个表状态，不足以判断表是否存在
    conn.create_table("test", {"cf":dict()})

table = conn.table('test')

for key, data in table.scan(filter=b"(ColumnPrefixFilter ('a')) OR (ColumnPrefixFilter ('b')) AND (ValueFilter (>=, 'binary:value3')) "):
    print(key, data)

# 分页限定符
for key, data in table.scan(filter=b"PageFilter (100)", include_timestamp=True):
    print(key, data)

conn.delete_table(b"test", disable=True)
