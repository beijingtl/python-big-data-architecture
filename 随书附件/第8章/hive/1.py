from pyhive import hive

with hive.connect(host="master1", port="10000") as cnn:
    cursor = cnn.cursor()
    _sql = """CREATE DATABASE IF NOT EXISTS imdb_movies"""
    cursor.execute(_sql)

    _sql = """CREATE TABLE IF NOT EXISTS imdb_movies.test (
        name string COMMENT "your name",
        age int COMMENT "your age")"""
    cursor.execute(_sql)

    _sql = """show tables in imdb_movies"""
    cursor.execute(_sql)
    _res = cursor.fetchall()
    print(_res)


with hive.connect(host="master1", port="10000") as cnn:
    cursor = cnn.cursor()
    _sql = """INSERT INTO TABLE imdb_movies.test
        VALUES ("zhangsan", 21), ("lisi", 24), ("wangwu", 27)"""
    cursor.execute(_sql)
    
    cursor.execute("SELECT * FROM imdb_movies.test")
    _res = cursor.fetchall()
    print(_res)
    

from TCLIService.ttypes import TOperationState
with hive.connect(host="master1", port="10000") as cnn:
    cursor = cnn.cursor()
    _sql = """INSERT INTO TABLE imdb_movies.test
        VALUES ("zhangsan", 21), ("lisi", 24), ("wangwu", 27)"""
    cursor.execute(_sql, async_=True)

    status = cursor.poll().operationState
    while status in (TOperationState.INITIALIZED_STATE, TOperationState.RUNNING_STATE):
        logs = cursor.fetch_logs()
        for message in logs:
            print(message)
        status = cursor.poll().operationState
    
    cursor.execute("SELECT * FROM imdb_movies.test")
    _res = cursor.fetchall()
    print(_res)



with hive.connect(host="master1", port="10000") as cnn:
    cursor = cnn.cursor()
    cursor.execute("DROP TABLE imdb_movies.test")

    cursor.execute("show tables in imdb_movies")
    print(cursor.fetchall())