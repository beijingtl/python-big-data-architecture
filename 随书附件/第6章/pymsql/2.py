import pymysql

connection = pymysql.connect(host='localhost', user='root', password='<Your-Root-Password>', database='examples', autocommit=None)

def do_something():
    raise Exception("Some trouble.")

with connection:
    with connection.cursor() as cursor:
        cursor.execute("CREATE TABLE IF NOT EXISTS users2 (`name` varchar(255) NOT NULL,`year` int NOT NULL);")
        try:
            connection.begin()
            insert_sql = "INSERT INTO users2 (`name`, `year`) VALUES (%s, %s)"
            cursor.executemany(insert_sql, [('张三', 36), ('李四', 32), ('王五', 31)])
            cursor.execute("select * from users2;")
            print("结果1: ", cursor.fetchall())
            do_something()
            connection.commit()
        except Exception as err:
            print(f"[×] 捕获到异常，执行回滚，异常：{err}")
            connection.rollback()
        cursor.execute("select * from users2;")
        print("结果2: ", cursor.fetchall())