from client_simple import Client
import time

c = Client()
while True:
    time.sleep(1)
    print(c.consume())