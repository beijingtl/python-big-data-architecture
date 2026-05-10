import pymysql.cursors

connection = pymysql.connect(host='localhost',
    user='root', password='<Your-Root-Password>', database='examples',
    cursorclass=pymysql.cursors.DictCursor)
    
with connection:
    with connection.cursor() as cursor:
        cursor.execute("select * from users4;")
        print("结果: ", cursor.fetchall())
