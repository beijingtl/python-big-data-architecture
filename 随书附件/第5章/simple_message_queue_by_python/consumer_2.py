from client import Client
import time

c = Client()
i = 0 
while True:
    time.sleep(0.1)
    print(c.consume())
    i =  i + 1