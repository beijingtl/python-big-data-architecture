import pika
connection = pika.BlockingConnection(  # 与 RabbitMQ 服务器构建连接
    pika.ConnectionParameters(host='some-rabbit'))
channel = connection.channel()  # 创建一个信道

channel.queue_declare(queue='hello')  # 声明一个队列

channel.basic_publish(  # 发送消息 "Hello World!"
    exchange='', 
    routing_key='hello', 
    body='Hello World!')
connection.close()  # 关闭连接


