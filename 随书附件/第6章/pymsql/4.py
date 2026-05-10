import sys, random, time, pymysql

all_data = [("".join(random.sample('zyxwvutsrqponmlkjihgfedcba',16)), random.randint(1,100)) for i in range(1000 * 10000)]

connection = pymysql.connect(host='localhost', user='root', password='<Your-Root-Password>', database='examples')

with connection:
    with connection.cursor() as cursor:
        cursor.execute("CREATE TABLE IF NOT EXISTS users3 (`name` varchar(255) NOT NULL,`year` int NOT NULL);")
        insert_sql = "INSERT INTO users3 (`name`, `year`) VALUES (%s, %s)"
        cursor.executemany(insert_sql, all_data)
    connection.commit()