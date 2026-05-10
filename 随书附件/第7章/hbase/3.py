import happybase
conn = happybase.Connection(host='localhost', port=9090)
if not b"test" in conn.tables():
    conn.create_table("test", {"cf":dict()})

table = conn.table('test')

table.put("row_test", {b'cf:a': bytes([3])})

[i for i in table.scan()]

table.row("row_test")
[i for i in table.row("row_test").values()][0]