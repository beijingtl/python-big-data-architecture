import pymysql

connection = pymysql.connect(host='localhost', user='root', password='<Your-Root-Password>')

with connection:
    with connection.cursor() as cursor:
        cursor.execute("CREATE DATABASE examples;")
        cursor.execute("CREATE TABLE examples.users (`name` varchar(255) NOT NULL,`year` int NOT NULL);")
        insert_sql = "INSERT INTO examples.users (`name`, `year`) VALUES (%s, %s)"
        cursor.executemany(insert_sql, [('张三', 36), ('李四', 32), ('王五', 31)])
    connection.commit()

    with connection.cursor() as cursor:
        cursor.execute("select * from examples.users where year > 31;")
        result = cursor.fetchall()
        print(result)