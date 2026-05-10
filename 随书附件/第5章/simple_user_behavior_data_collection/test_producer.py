import time
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers=['localhost:32772'])

def on_send_success(r):
    print(f"{time.time()}, {r.timestamp/1000}")

for _ in range(5):
    fur = producer.send('hello2', b'msg')
    r = fur.add_callback(on_send_success)

for _ in range(5):
    fur = producer.send('hello', b'msg')
    r = fur.get(timeout=5)
    print(f"{time.time()}, {r.timestamp/1000}")







def on_send_success(r):
    print(f"{time.time}, {r.timestamp/1000}")

def on_send_error(excp):
    print('I am an errback', excp)

for _ in range(4):
    fur = producer.send('hello', b'msg')
    fur.add_callback(on_send_success).add_errback(on_send_error)

import time
def callback(i, idx):
    print(f"i am ok. {time.time()}, {i.timestamp}, msg{idx}.")

for _ in range(20):
    print(f"send, {time.time()}, msg{_}")
    fur = producer.send("hello", f"[msg{_}] hello,world!".encode("utf-8"))
    fur.add_callback(callback, idx=_)


for _ in range(10):
    future = producer.send("hello", b"hello,world!")
    a = future.get(timeout = 6)
    print(a)
    # furture 会同步发送。


# get timeout 单位秒
fur.get(timeout=10)

producer.flush()

record_metadata = fur.get(timeout=10)