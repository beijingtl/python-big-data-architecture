import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', 9999))

with open("longlong.txt", "r", encoding="utf-8") as f:
    data = f.read()

bdata = data.encode("utf-8")

# 尝试往此时尚未 accept 的 socket 中循环插入数据
s.send(b"Hi,I'm coming!")

s.send(bdata)

for i in range(1000):
    s.send(b"hellohellohello")
    # 这块也可以看出一些端倪来，如果 recv 是在 send 后瞬间进行的，那么一千次 send 对应的应该就是一千次 recv 但是实际上有 50 
    # 也就是说send了20条，然后recv了1条，大致这个频率
    # 218 283 335 437 511(发送的数据很短) 889（发送的数据很长）
    