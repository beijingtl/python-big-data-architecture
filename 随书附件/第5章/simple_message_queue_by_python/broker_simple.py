import queue

class BrokerQueue:
    def __init__(self):
        self.__q = queue.Queue()

    def produce(self, msg):
        self.__q.put_nowait(msg)
        print(f"[√] 向消息队列添加一条消息: {msg[:30]}")

    def consume(self):
        try:
            msg = self.__q.get(block=True, timeout=5)
            print(f"[√] 消费消息: {msg[:30]}")
            return msg
        except queue.Empty:
            print(f"[x] 超时，消息队列已空，暂无可需处理消息")


import threading, socket

class BrokerServer(BrokerQueue):
    def __init__(self, service_ip='localhost', service_port=9999):
        super(BrokerServer, self).__init__()
        self.service_ip = service_ip
        self.service_port = service_port

    def handle(self, sock, addr):
        print(f"[√] 接受来自 {addr} 的新连接.")
        data = sock.recv(1024)
        method, body = data.decode("utf-8").split(sep="\r\n\r\n", maxsplit=1)
        if method == "Produce":
            print(f"[*] 生产消息...")
            while True:
                data = sock.recv(1024)
                body = body + data.decode("utf-8")
                if not data:
                    break
            self.produce(body)
        elif method == "Consume":
            print(f"[*] 消费消息...")
            msg = self.consume()
            msg and sock.send(msg.encode("utf-8"))
        sock.close()
        print(f"[√] 关闭来自 {addr} 的连接\n")

    def run(self):
        __s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        __s.bind((self.service_ip, self.service_port))
        __s.listen() 
        print("[*] 等待连接...")
        try:
            while True:
                sock, addr = __s.accept()
                t = threading.Thread(target=self.handle, args=(sock, addr))
                t.daemon = True
                t.start()
        except KeyboardInterrupt:
            __s.close()
            print("[x] 停止服务")

if __name__ == "__main__":
    broker_server = BrokerServer()
    broker_server.run()
