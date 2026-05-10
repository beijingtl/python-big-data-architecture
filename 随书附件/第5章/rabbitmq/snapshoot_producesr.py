import pika

with pika.BlockingConnection(pika.ConnectionParameters(host='localhost')) as conn:
    channel = conn.channel()  # 创建一个信道
    channel.queue_declare(queue='snapshoot_regularly_schedule')  # 声明一个队列

    channel.basic_publish(
        exchange='', 
        routing_key='snapshoot_regularly_schedule', 
        body="test"
    )


