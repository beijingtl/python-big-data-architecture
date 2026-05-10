import socket, queue, threading

class BrokerQueue:
    def __init__(self, maxsize):
        self.QUEUE_MAX_SIZE = maxsize # 消息队列的最大容量
        self.__q = queue.Queue(maxsize = self.QUEUE_MAX_SIZE) # 创建一个FIFO（先进先出）队列

    def produce(self, msg):
        """生产消息"""  
        try:
            self.__q.put_nowait(msg) # 生产消息，不能让其阻塞，不然回导致消息队列已满的情况下，线程不断增长
            print(f"[√] 向消息队列添加一条消息: {msg[:30]}，当前消息队列数：({self.__q.qsize()}/{self.__q.maxsize})")
        except queue.Full:
            print(f"[x] 消息队列可处理的消息已达到最大符合，无法继续放入消息")

    def consume(self):
        """消费消息"""
        try:
            msg = self.__q.get(block=True, timeout=5) # 消费消息，当消息队列为空时阻塞，如果始终没有消息可以消费，则在30s后抛出超时错误
            print(f"[√] 消费消息: {msg[:30]}. 当前消息队列数：({self.__q.qsize()}/{self.__q.maxsize})")
            return msg # 当有消息时返回接收的消息，否则该函数无返回（返回为空）
        except queue.Empty:
            print(f"[x] 超时，消息队列已空，暂无可需处理消息")


class BrokerServer:
    """构建服务端，负责与客户端通信"""
    def __init__(self, service_ip='localhost', service_port=9999, queue_max_size=3):
        self.service_ip = service_ip
        self.service_port = service_port
        self.q = BrokerQueue(queue_max_size) # 构建队列实例

    def handle(self, sock, addr):
        """解析并处理从Client收到的消息"""
        print(f"[√] 接受来自 {addr} 的新连接.")
        data = sock.recv(1024) # 接收数据，我们期望首次接收的数据中，包含了我们定义的方法信息
        method, body = data.decode("utf-8").split(sep="\r\n\r\n", maxsplit=1)
        if method == "Produce": # 如果请求的方法是 Produce 即生产消息，则继续接收消息，这里我们相当于声明了一个简单的协议，即使用 \r\n\r\n 来分割消息中的方法和正文内容。
            print(f"[*] 生产消息...")
            while True:
                data = sock.recv(1024) # 每次接受 1024 字节
                body = body + data.decode("utf-8")
                if not data: # 即客户端发送完毕，并关闭端口，此时 recv 返回 b''
                    break
            self.q.produce(body)
        elif method == "Consume": # 如果请求为消费，则不考虑其他包括 body_lenght, body 直接从队列中获取消息并返回
            print(f"[*] 消费消息...")
            msg = self.q.consume()
            msg and sock.send(msg.encode("utf-8")) # 如果 msg True 则发送编码后 msg
        sock.close()
        print(f"[√] 关闭来自 {addr} 的连接\n")

    def run_win(self):
        """运行 Server""" 
        __s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        __s.bind((self.service_ip, self.service_port))
        __s.listen() # 启动一个服务器用于接受连接
        __s.settimeout(1)
        print("[*] 等待连接...")
        try: # 适用于 Win 环境下使用 CTRL+C 中止程序
            while True:
                try:
                    sock, addr = __s.accept() # 接受一个新连接
                    t = threading.Thread(target=self.handle, args=(sock, addr)) # 创建新的线程来处理接受的连接
                    t.daemon = True # 当程序剩下的线程都主线程是，整个 Python 程序将会退出 
                    t.start()
                except socket.timeout:
                    pass
        except KeyboardInterrupt:
            __s.close()
            print("[x] 停止服务")

    def run_linux(self):
        """运行 Server 在 Linux 上
        此处的区别在于 Window 下上述程序无法通过 CTRL+C 关闭
        """
        __s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        __s.bind((self.service_ip, self.service_port))
        __s.listen() # 启动一个服务器用于接受连接
        print("[*] 等待连接...")
        try: # 适用于 Win 环境下使用 CTRL+C 中止程序
            while True:
                sock, addr = __s.accept() # 接受一个新连接
                t = threading.Thread(target=self.handle, args=(sock, addr)) # 创建新的线程来处理接受的连接
                t.daemon = True # 当程序剩下的线程都主线程是，整个 Python 程序将会退出 
                t.start()
        except KeyboardInterrupt:
            __s.close()
            print("[x] 停止服务")

if __name__ == "__main__":
    broker_server = BrokerServer()
    import platform
    print(f"platform is {platform.platform()}.")
    if 'Window' in platform.platform():
        broker_server.run_win() # 注，在 CMD 中生效，但是在 VSCode 中不生效
    else:
        broker_server.run_linux()


