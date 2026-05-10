import pika, sys, os, time, datetime, random

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='snapshoot_regularly_schedule')
    channel.basic_qos(prefetch_count=5)
    
    def callback(ch, method, properties, body):
        print(f"{datetime.datetime.now()} [x] 收到消息 {body}")
        time.sleep(20*random.random())

    channel.basic_consume(queue='snapshoot_regularly_schedule', on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)