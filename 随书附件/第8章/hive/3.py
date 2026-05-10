from pyhive import hive

cursor = hive.connect(host="master1", port="10000").cursor()

_sql = "SELECT RAND()"
cursor.execute(_sql)
print(cursor.fetchall())

_sql = "SELECT FLOOR(1.6), CEIL(1.6), BROUND(1.5)"
cursor.execute(_sql)
print(cursor.fetchall())

_sql = "SELECT LN(EXP(2)), LOG2(4), POW(2,3), SQRT(16)"
cursor.execute(_sql)
print(cursor.fetchall())

_sql = "SELECT BIN(31), HEX(31)"
cursor.execute(_sql)
print(cursor.fetchall())

_sql = "SELECT unix_timestamp(), unix_timestamp('2021-11-07 17:30:01'), unix_timestamp('21/11/07 17:30', 'yy/MM/dd hh:mm')"
cursor.execute(_sql)
print(cursor.fetchall())

_sql = "SELECT current_date(), date_add(current_date(), 30), datediff(current_date(), date_add(current_date(), 30))"
cursor.execute(_sql)
print(cursor.fetchall())

_sql = "SELECT title, date_published, floor(datediff(current_date(), date_published)/365) FROM imdb_movies.ods_movies LIMIT 5"
cursor.execute(_sql)
print(cursor.fetchall())

_sql = "SELECT ltrim(' zs '), rtrim(' ls '), trim(' ww ')"
cursor.execute(_sql)
print(cursor.fetchall())

# https://www.kaggle.com/stefanoleone992/imdb-extensive-dataset

_sql = "SELECT parse_url('https://www.kaggle.com/?test=stefanoleone992#imdb-extensive-dataset', 'QUERY')"
cursor.execute(_sql)
print(cursor.fetchall())

_sql = 'SELECT split("zhang san", " ")'
cursor.execute(_sql)
res = cursor.fetchall()

sql = 'SELECT * from test'
cursor.execute(_sql)
res = cursor.fetchall()