import socket, select

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('127.0.0.1', 9999))
s.listen(5)
# s.setblocking # 设置端口为阻塞(true)或非阻塞(false) 等同于 settimeout(None) -> blocking / settimeout(0.0) -> non-blocking
# s.fileno() # 返回端口的文件描述符（一个低位数字，例如 13），这对于 select.select() 很有用

epoll = select.epoll() # 返回一个 epolling 对象
# select.EPOLLIN | select.EPOLLET 
# 一个是IN，一个是ET
# epoll 的知识，对于理解 redis 的异步IO多路复用很有帮助。