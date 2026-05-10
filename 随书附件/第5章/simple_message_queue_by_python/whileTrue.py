import time,sys

try:
    while True:
        time.sleep(10)
except KeyboardInterrupt as err:
    print(f"[x] stop server.")
    sys.exit(0)



