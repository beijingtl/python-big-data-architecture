import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 监听端口:
s.bind(('127.0.0.1', 9999))
s.listen(5)
print('Waiting for connection...')

sock, attr = s.accept()
buffer = []
i = 0 
while True:
    print(f"[{i}] times recv.")
    data = sock.recv(1024) # 这块问题在于，后面一次 recv 的时候，阻塞了。
    if data and i < 1000:
        buffer.append(data)
        i = i + 1
    else:
        break

# 设置为非阻塞模式
sock.setblocking(False)
# 非阻塞模式下，如果 recv 没有对应的数据，则返回 BlockingIOError: [WinError 10035] 无法立即完成一个非阻止性套接字操作。
