from kafka import KafkaConsumer
import time, json
consumer = KafkaConsumer('collection',
    bootstrap_servers = ['192.168.0.52:32779', '192.168.0.52:32778'],
    group_id = "cg_2"
)
for msg in consumer:
    _msg = json.loads(msg.value.decode("utf-8"))
    _t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(_msg["st"])/1000))
    print(f"收到用户行为数据：\n\t网页：{_msg['dh']}\n\t事件类型：{_msg['t']}\n\t触发时间：{_t}\
        \n\t客户端ID：{_msg['ccid']}\n\t设备UA：{_msg['ua']}")