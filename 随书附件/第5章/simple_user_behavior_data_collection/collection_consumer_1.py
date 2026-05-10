from kafka import KafkaConsumer
consumer = KafkaConsumer('collection',
    bootstrap_servers = ['192.168.0.52:32779', '192.168.0.52:32778'],
    group_id = "cg_1"
)
for msg in consumer:
    with open('collection.txt', 'a+') as f:
        f.write(msg.value.decode("utf-8")+"\n")