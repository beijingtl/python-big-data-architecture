from client_simple import Client
import time

c = Client()
for i in range(100):
    time.sleep(0.01)
    c.produce(f"msg[{i}]")