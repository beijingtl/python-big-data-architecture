'''hello,world for rabbitmq 
receiving part
'''
import pika, sys, os

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='some-rabbit'))
    channel = connection.channel()

    channel.queue_declare(queue='hello')
    channel.basic_qos(prefetch_count=5)
    
    def callback(ch, method, properties, body):
        print(" [x] 收到消息 %r" % body)
    channel.basic_consume(queue='hello', on_message_callback=callback, auto_ack=True)
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