# 概述
一个基于 Python 的简易消息队列实现。

# Command
## Docker
```s
docker run --name python-dev -v C/Users/14606/Desktop/写书/simple_message_queue_by_python:/home/py_dev -w /home/py_dev -dit python:3.8.5 /bin/sh 
```


# 思路
1. 一个完整的消息队列，至少包含三个角色，两个模块：
    - broker
        - 消息处理中心
            - 包含一个容器（即队列），可以用于存储消息
            - 在接收到生产者的消息，后将消息存储在容器中
            - 在接收到消费者消费的请求时，将消息发送给消费者
    - client
        - 消息生产者
            - 将消息发送给消息处理中心
        - 消息消费者
            - 向消息处理中心请求，获取消息
2. 通信
    - 使用 TCP 协议进行通信
    - 这里面，设置成 client 主动向 broker 发送请求
3. 最终实现效果
    - 客户端既可以将自己设置为 publisher 角色，也可以将自己设置为 consumer 角色

# 杂记
1. socket 是计算机网络中用于在节点内发送或接收数据的内部端点。具体来说，它是网络软件 (协议栈) 中这个端点的一种表示，包含通信协议、目标地址、状态等，是系统资源的一种形式。
    - socket 的诞生是为了应用程序能够更方便的将数据经由传输层来传输，所以它本质上就是对 TCP/IP 的运用进行了一层封装，然后应用程序直接调用 socket API 即可进行通信。
        - socket 是应用层和传输层之间的一个抽象层
        - 服务器和客户端各自维护一个"文件"，在建立连接打开后，可以向自己文件写入内容供对方读取或者读取对方内容，通讯结束时关闭文件。
            - 写入的内容，在文件中，就是一串连续的数据，对于数据的分割，是从协议上进行的，比如约束沙沙表示开始，表示结束。
    - 参考文档：https://www.zhihu.com/question/29637351
    - ![socket](https://pic4.zhimg.com/80/v2-b74b6c43650343350ab89cfae304689e_720w.jpg?source=1940ef5c)
        - 这张图的形式可以，可以借用
        - 后面的图也不错
    - 发送缓冲区和接收缓冲区就是套接字缓存（socket buffer）
    - TCP/IP 的连接关闭过程比粗行家更复杂一些，四次握手
        - <note>所以这就是为什么要维护信道 channel 的原因，这样可以减少 TCP/IP 连接/关闭 的损耗。
    - Linux 网络核心数据结构是套接字缓存（socket buffer），表示一个要发送或处理的报文。
        - 组成：
            - 报文数据：它保存了实际在网络中传输的数据；
            - 管理数据：供内核处理报文的额外数据，这些数据构成了协议之间交换的控制信息。
2. TCP 创建的是双向通道，具体由谁先发数据，以及发什么数据，由协议来决定。
    - `socket.rece(buffersize)`
        - 从套接字接收最多buffersize字节。对于可选标志参数，请参阅Unix手册。当没有可用数据时，阻塞直到至少有一个字节是可用的，或者直到远程端关闭为止。当关闭远端，读取所有数据，返回空字符串。
        - 这里通过一个循环来获取数据，如果获取的为空，则表示接收完毕，退出循环。
    - 这块需要注意的是，socket 开始 listen 后，还需要通过 accept 来接收连接。
        - `s.listen(backlog)`
            - 允许服务器接受连接。如果指定了backlog，它必须至少为0(如果它更低，则设置为0);它指定系统在拒绝新连接之前允许的未接受连接的数量。如果未指定，则选择一个合理的默认值。
            - `ConnectionRefusedError: [WinError 10061] 由于目标计算机积极拒绝，无法连接。`
                - 注意，这块的 listen backlog 是允许的 “未接受连接的数量” 也就是说，没有通过 accept 接受的 connect 数量，accept 的就不包含在其内了。（当然，如果 accept 了，就又空出来了，这相当于提供了一个缓冲区，避免一瞬间涌入过多连接。）
    - `sock, addr = s.accept()` 
        - return socket object, address info
            - socket object 一样是一个 socket 但是和一开始构建的 socket 有些区别
                - `s -> <socket.socket fd=1304, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM, proto=0, laddr=('127.0.0.1', 9999)>`
                - `socket -> <socket.socket fd=1528, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM, proto=0, laddr=('127.0.0.1', 9999), raddr=('127.0.0.1', 63810)>`
                - 可以看到，连接后返回的 sock 多了一个 raddr 
        - 等待一个传入的连接（在没有收到新连接时会阻塞，直到收到新的连接位置）
    - `s.recv(num)` 像流一样读取接收数据。
        - `OSError: [WinError 10057] 由于套接字没有连接并且(当使用一个 sendto 调用发送数据报套接字时)没有提供地址，发送或接收数据的请求没有被接受。`
            - 所以负责 binding 的这个 socket 不管连接，连接的是 accept 返回的那个 socket
            - 连接建立后，就可以发送了，可以一直发。
                - <why>问题是，这块 send / recv 没有有一个上限吗？支持一直不停的发送吗？或者说，这块的缓冲区大小是多少。
            - send 会返回已发送的字节数。
    - 已经关闭的 socket 在另一端还可以进行数据的发送，但是在已关闭这一端就不能继续发送数据了。
        - 会显示为 closed `<socket.socket [closed] fd=-1, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM, proto=0>`
        - 不是，应该是我一开始在 server 上 binding 了一个端口
        - 然后 client 连接 server
        - server 接收连接，并返回一个新的 socket，这个 socket 中包含了 client 的 ip/端口等信息，可以通过这个 socket 向 client 发送数据。
        - 我关闭了 server 端的端口，但是此时我只是无法通过 server 向 client 发送数据了，但是此时 client 到我端口的连接还是有的。    
            - s_server -> 建立 binding 的端口 `<socket.socket fd=968, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM, proto=0, laddr=('127.0.0.1', 9999)>`
            - s_accept -> s.accept 返回的端口 `<socket.socket fd=976, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM, proto=0, laddr=('127.0.0.1', 9999), raddr=('127.0.0.1', 64531)>`
            - s_client -> 客户端连接 9999 端口的 `<socket.socket fd=1388, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM, proto=0, laddr=('127.0.0.1', 64531), raddr=('127.0.0.1', 9999)>`
            - 如果我此时再创建一个新的连接。
                - `<socket.socket fd=3200, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM, proto=0, laddr=('127.0.0.1', 64644), raddr=('127.0.0.1', 9999)>`
                - 可以看到使用另外一个随机的端口进行了请求
        - 这块很奇怪是，我第一次是 accept 阻塞了，后一次我没有用 accept 但是请求也成功了。
            - 应该是如果没有发起的 connection 请求，才会阻塞。
            - 而且这块的 accept 类似一个 FIFO 队列的形似    
                - 根据连接的先后顺序来进行弹出。
            - 另一个问题是，我 listen 是应该设置了 5 但是不知道为啥一直可以连接。
                - 奇怪我这次没有设置 accept 但是还是正常接收了 client 的 connection 请求，没有显示服务器积极拒绝。
            - `OSError: [WinError 10056] 在一个已经连接的套接字上做了一个连接请求。` 对于一个已经连接的套接字不能再做连接请求
    - 关于套接字超时的说明
        - 一个套接字对象可以处于三种模式之一：阻塞、非阻塞或超时
            - 套接字默认以阻塞模式创建，可以调用 `setdefaulttimeout()` 来更改
            - 在 blocking 阻塞模式中，操作将阻塞，直到操作完成或系统返回错误（如连接超时）。
            - 在 non-blocking mode （非阻塞模式）中，如果操作无法立即完成，则操作将失败（不幸的是，不同系统返回的错误不同）：位于 select 中的函数可用于了解套接字何时以及是否可以读取或写入。
            - 在 timeout mode （超时模式）下，如果无法在指定的超时内完成操作（抛出 timeout 异常），或如果系统返回错误，则操作将失败。
    - <how>
        - 发送的一次请求，如果可以准确识别到请求是要求关闭连接呢？因为我是以流来进行发送的，用户无法在流中去准确识别我的一个流的结束，只能一直接收。
            - 例如，我从 client 发送数据，发送完毕了后，我发送一个 EXIT 消息给 server 告诉 server 我发完了。
            - 但是问题在于 server 端处理的速度是很快的，发送的时候如果没有一个明确的标识，我还是确定不了还是停止连接。
            - 以 HTTP 客户端的请求消息中，只有请求头+正文，没有说一个请求结尾，那么如何识别一个请求结束了呢？
            - 我可以在请求头中，标识需要发送的消息的长度，然后仅读取特定长度的消息即可。
            - 这块有个点就是，如果 SERVER 端没有发送 EXIT
                - 不用，直接就解析头部，获取完特定长度的数据，就直接关闭连接，不考虑后面客户端没有关闭连接，还想继续发送数据的情况。
            - 以新浪为例，请求后，没有阻塞，是因为 recv 一直有收到消息，欸，不对，是怎么做到一直保持 socket 有数的呢？
                - 怎么做到 RECV 一直有返回的？
                - 而且我在创建的 server 的时候，send b'' 是没有效果的，recv 依然保持阻塞。
                    - <note>此处的答案是，服务器端响应完毕后就关闭了连接，而此时客户端再接收就是 b'' 了。
                    - 不够此时 socket 还是可以继续发送数据的，但是没有太大意义了。
                    - <note>tcp 中，当一段收到一个 FIN 内核让 read 返回 0 来通知应用层另一端已经终止了向本端的数据发送。发送 FIN 通常是应用层对 Socket 进行关闭的结果。
    - 导致 CTRL+C 无法退出的原因有两，一是 __s.accept() 阻塞了，不能停止，而是 threading.Thread 
3. 测试
    - 不用考虑这么多，我们就直接一个生产者，一个消费者这种最简单的模型即可。
    - 线程这部分还是不能丢的，不然单线程阻塞运行连接，实在是太蠢了。
    - 消费时阻塞一下会不会比较好
    - 在接收数据时，我们不需要考虑发送数据的长度，应为客户端发送完毕，端口就关闭了，在 recv 就是 b'' 了。
4. 推模式与拉模式
    - 在设计的简易 Demo 中，client 发出一个 CONSUME 的请求，然后等待回传的消息，然后传递完毕后 Socket 就关闭了，这是一个简单的拉模式，由客户端发起。
        - 对比，如果客户端和 broker 建立了连接后，客户端发起 CONSUME 请求，但是没有在接收到一个消息后就关闭，而是持续等待，等待服务器向客户端发送请求，那就是推模式。
            - 所以如果想要实现推模式，那么服务端必须和客户端维持一个连接，以让服务端知道推送给谁。
5. select() / poll() 以 python
    - https://harveyqing.gitbooks.io/python-read-and-write/content/python_advance/how_to_use_linux_epoll.html 这篇文章讲的不错
    - <note>通常来说，python 程序binding的socket为主线程，每当一个新的客户端连接进来时，会调起一个新的线程来与之通信。因此每个线程只会与一个客户端通信，某个线程的阻塞并不会影响其他线程的正常运行。
        - 这个有些缺点，比如多线程的数据同步和单CPU线程的低效。其实可以这么理解，比如我们把 Socket 理解为一个个信箱假设我现有同时有1000个邮箱，都在正常运营，里面时不时会投递一下信件，服务器是邮局，邮局需要从邮箱中获取信件，那么我们现在的做法，简单来说，就是每个邮箱上分配一个人（线程），这个人在来信的时候，接收信件。但是可以看到，这样很愚蠢对吧，当然还有更愚蠢的方式，比如我不分配线程，而是由一个人（线程）挨个处理每个信箱，在等到消息的时候拉回邮局，这就是不使用多线程的方式。
            - 异步 socket 对异步 socket 的操作会立即返回成功或失败，（其实端口阻塞，更多是发生在等待过程，而不是读取过去，不过读取IO也是有一定的损耗） 
        - python 提供了 select / poll / epoll 三个 API，epoll & poll 比 select 高效。select 需要用户程序对每一个 socket 的事件进行检查，而另两个则可以依赖系统来获知那些 socket 正在发生指定的事件。
    - 使用异步 Socket 
    - epoll
        - `epoll_create(int size)` 创建一个epoll句柄，同时也占用一个文件描述符．size指明这个epoll监听的数目有多大．
            - 这块的 size 就是一个 hint 也就是一个提示/示意，内核会自动分配所有事件所需的内存。
        - `int epoll_ctl(int epfd, int op, int fd, struct epoll_event *event);` 用于向 epoll 注册一个事件，而且明确监听的事件类型
        - `int epoll_wait(int epfd, struct epoll_event * events, int maxevents, int timeout);`
            - 这个函数用于等待事件的发生，第二个参数是用户自己开辟的一块事件数组，用于存储就绪的事件，第三个参数为这个数组的最大值，就是第二个参数事件数组的最大值，用户想监听fd的个数，第四个参数为超时时间(0表示立即返回，-1表示永久阻塞，直到有就绪事件)
        

# Note
1. 注意：为什么 CTRL+C 在 window 下无法生效
    - 在 WIN 环境下，需要使用 CTRL+Break/Pause 来进行停止
        - 测试好像并没有效果
            - 是只有在 vscode 中没有效果，但是 cmd 和 Powershell 都是正常生效的
                - 测试应该是 vscode 的设置问题，自动忽略了一些命令，例如：commandsToSkipShell
        - > It turns out that as of Python 3.6, the Python interpreter handles Ctrl+C differently for Linux and Windows. For Linux, Ctrl+C would work mostly as expected however on Windows Ctrl+C mostly doesn't work especially if Python is running blocking call such as thread.join or waiting on web response. It does work for time.sleep, however. Here's the nice explanation of what is going on in Python interpreter. Note that Ctrl+C generates SIGINT.
2. 我本章一开始，我们很轻易地接受了 broker 消息掮客/消息处理中心的这么一个存在，但是除了 broker 这种常规架构外，类似 zeromq 还提供了 brokerless 的架构。
    - 每个zeromq套接字都有发送和recv队列(限制通过高水位标记设置)。
3. 在示例中，我们设置的 QUEUE_MAX_SIZE 其性质，很像是一个高水位设置，超过这个上限的消息，就将被自动丢弃，而不会被消费。
4. Demo 存在的问题
    - 内部只有一个 Queue，但是实际中，我们希望有多个 Queue，并可以在发送消费时指定去那个 Queue
    - 基于 Python 性能很差，比如多线程那部分
    - 支持的消息类型有限，目前只有字符串
    - 客户端通过发送消费请求来获取数据，如果单次还好，但是如果是一个 While True: 的循环，那么会造成很大的性能积压，即使我们设置了连接上限也是一个问题。（会抛出错误的）
        - 我可不可以设置三个 Client 一个不停的生产，另外两个不停的消费。
    - 如果消息队列已满，我们可能会希望让消息回退给我们，或者等待消息队列空出位置，而不是直接抛弃，甚至可能希望让优先级高得消息先入列等等。
    - 我们或许想要考虑分布式得场景，虽然现在得 Demo 使用 TCP 支持这种跨主机得服务，但是对于分布式肯定是远远不够得，我们希望可以让消费者服务器自由得加入/退出，被服从管理，根据性能得差异来进行消息得消费。
    - QUEUE_MAX_SIZE 的设置，约束了队列可以接收的信息的大小，但是对于消息本身的长度没有约束，且理想情况下，我们应该允许队列尽可能的大，但是又要防止内存溢出，当内存放不下的时候，自动放到硬盘或其他存储介质中。
    - 对于生产者来说，没有等待服务端的生产成功响应就断开了，这意味很大概率会丢数。
5. Exchange 出现得场景是，broker 中不可能只存在一个 Queue，那么如何将消息发送至正确得 Queue 呢？
    - 这就是 Exchange 发挥得地方，Exchange 相当于一个规则表，约束了该如何发送数据至队列。  
        - 常见的 Exchange 包括 direct / fanout / topic / headers ...
6. 啥是多路复用？   
    - 这个IO多路复用，跟之前的异步IO似乎是一个玩意，就是单拎一个线程出来，专门用来监控状态，就状态符合要求的，单独开启一个线程处理即可。这样就减少了线程的内存开销和上下文切换的CPU开销。
        - I/O多路复用技术（multiplexing）是什么？ - 用心阁的回答 - 知乎 https://www.zhihu.com/question/28594409/answer/74003996
    - 其实可以以 DEMO 来思考，在设计的 DEMO 中，一个线程处理一个连接，如果同时有很多个连接接入，但是又阻塞着让消息无法处理完毕。那么就会造成同时在CPU里n多线程挂着，这样肯定是不行的，光线程的开销是吃不消了。那咋办？用一个线程，在每个SOCKET连接时记录一下，然后用这个线程去轮询所有Socket的状态，如果有数据，就开启一个线程来处理，如果没有就继续循环着，这样系统中存在的线程数就少的多了。
        - 这块如果是端口连接了，需要找到端口对应的处理方法，需要循环遍历寻找，就是 SELECT
        - epoll 极大的提高了并发性能
    - epoll 的实现机制
        - epoll 在被内核初始化时（操作系统启动时）同时会开辟出 epoll 自己的内核告诉 cache 区（连续的物理内存页），用于安置每一个我们想监控的 socket
            - 这些 socket 会以红黑树的形式保存在内核 cache 里，以支持快速的查找/插入/删除
            - https://blog.csdn.net/lixungogogo/article/details/52226479 <note> 这部分关于 epoll 的实现原理写的不错
    - I/O 一般就是文件系统的读写/网路请求端口的读写
        - 这个理解是不对的，I/O 的场景很多
7. 通过 docker network 创建的网络，是如何将容器名称指向对应容器IP的  
8. 啥是 I/O 多路复用技术 multiplexing，Linux 中的 select / poll / epoll 是干什么用的？
    - 操作系统为你提供了一个功能，当你的某个 socket 可读或者可写的时候，它给你一个通知，这样当配合非阻塞的 socket 使用时，只有当系统通知我哪个描述符可读了，我才去执行read操作，可以保证每次read都能读到有效数据而不做纯返回-1和EAGAIN的无用功。写操作类似。
    - select / poll / epoll 都是 IO 多路复用的机制。
9. 推拉模式的区别
    - pull 拉，主动消费类型
    - push 推，被动消费类型
10. <key>rabbitmq / kafka / zeromq 彼此之间都有很大的差异，可以在最开始描述消息队列的通用性，然后在后续章节，将不同程序的特殊之处
    - 对于一个消息队列来说，最基本的构成是 Producer 生产者 / queueu 队列 / consumer 消费者
        - 然后根据 queue 所处在的位置，可以区分，比如 zeromq 中默认 queue 是在 prodcuer 或 consumer 中的，而如 rabbitmq 则将 queue 放在了 broker 中。
            - <q>那么 kafka 中的 queue 在哪里呢？
                - 应该也是 broker，broker 将消息将收到的消息存储到磁盘中
    - 同时 producer / consumer 的数量也会发生变化。
        - 比如一个 producer 对应多个 consumer fanout 
        - 一个 consumer 对应多个 producer fanin 
        - 多个 producer 对应多个 consumer ？？
        - 一个 producer 对应一个 consumer ？？
11. <note>消息的传递，只是一个中间过程，并不是说收到消息就完了，反而，收到消息后很多复杂麻烦的事务才开始正式进行，比如数据的计算/分析/清洗/转换/入库等等。
12. Kafka
    - Kafka 中的消息是以主题未基本单位进行归类的，各个主题在逻辑上相互独立。    
        - <note> 与主题类似的概念是 AMQP 中的队列，AMQP 中的队列是逻辑独立的。 
            - <q> 但是应该还是有所不同的，主题/分区/队列这种设计，应该是从分布式的角度去考虑的。此处可以仔细对比一下
13. 消息协议
14. 选型
    - 假设我们现在有个用户行为日志收集系统，负责收集我们网站上的用户行为数据，我们按月计算的数据量大约在10E级别，也就是说一个月大概总共有近10E的数据，会发送至我们的系统。10E这个数据规模很大，但是对于选型，或者架构设计来说，我们并不关心其总量的担心，而关心1S的数据，则：
        - 10E/30 ~ 1天约 3000w 条数据，一天有 86400s，则每秒平均处理 347 条数据，按照峰值一般取平均值的3倍左右，则峰值大概在1000条请求/秒。
            - 这个量级的数据，基本上大部分的消息队列都可以支持了，无论是 Kafka 还是 rabbitmq 还是 zeromq
            - 即使考虑到业务会增长，我们需要留一定的余量，大概峰值*4 左右，不过其实没有必要了。
                 - QPS 一台服务器每秒能够响应的查询次数
                 - TPS 事务数/秒。事务包括：用户请求服务器 - 服务器自己的内部处理 - 服务器返回给用户
        - 从高性能 / 高可用 / 高可拓展性几个层面考虑。有的，例如金融行业，还需要考虑安全性等。对于中心企业，可能还会衡量成本，开源协议等等。