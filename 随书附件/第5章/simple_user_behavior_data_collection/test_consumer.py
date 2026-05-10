from kafka import KafkaConsumer
consumer = KafkaConsumer('hello2',
    bootstrap_servers = ['192.168.0.45:32773', '192.168.0.45:32774'],
    group_id = "group_1"
)
for msg in consumer:
    print(msg)