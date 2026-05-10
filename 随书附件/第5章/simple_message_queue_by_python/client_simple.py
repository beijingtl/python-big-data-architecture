import socket

class Client:
    """定义一个消息队列客户端，支持消息的生产及消息
    """
    def __init__(self, service_ip='localhost', service_port=9999):
        self.service_ip = service_ip
        self.service_port = service_port

    def produce(self, msg):
        print(f"[*] 生产消息...")
        __s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        __s.connect((self.service_ip, self.service_port))
        __s.send(f"Produce\r\n\r\n{msg}".encode("utf-8"))
        __s.close()
        print(f"[√] 消息生产完毕，关闭连接")

def consume(self):
    print(f"[*] 消费消息...")
    __s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    __s.connect((self.service_ip, self.service_port))
    __s.send(f"Consume\r\n\r\n".encode("utf-8"))
    print(f"[*] 发送消费请求...")
    buffer = []
    while True:
        _d = __s.recv(1024)
        if _d:
            buffer.append(_d)
        else:
            break
    msg = b"".join(buffer).decode("utf-8")
    print(f"[√] 获取到待消费消息，关闭连接")  if msg else print(f"[x] 超时，未获取到待消费消息，关闭连接") 
    __s.close()
    return msg

if __name__ == "__main__":
    pass

