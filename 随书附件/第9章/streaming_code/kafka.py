
# 生产-用于source交互执行-手动模式
from kafka import KafkaProducer
producer = KafkaProducer(bootstrap_servers=['localhost:32768', 'localhost:32769', 'localhost:32770'])
producer.send('words1', b'This is the first word')
producer.send('words2', b'This is the second word')


# 生产-用于source交互执行-持续自动模式
from kafka import KafkaProducer
import random
producer = KafkaProducer(bootstrap_servers=['localhost:32768', 'localhost:32769', 'localhost:32770'])
while True:
    row_num = random.randint(1,20)
    producer.send('words1', bytes(f'This is the {row_num} word', encoding="utf8"))


# 消费-用于sink交互展示
from kafka import KafkaConsumer
consumer = KafkaConsumer('streaming_sink',bootstrap_servers=['localhost:32768', 'localhost:32769', 'localhost:32770'])
for msg in consumer:
    print(msg)