import pika
import json
import time

host = "node0.cl-dev-mqcluster-sdp-rabbitmq-api-sraohm.docker.sdp"
port = 7247
credentials = pika.PlainCredentials('sdp-rabbitmq-api', 'FolnEhAFdxN4')
connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port, credentials = credentials))
 
channel = connection.channel()

exchange_name = "exchange2"
queue_name = "test-log"
# channel.exchange_declare(exchange=exchange_name, exchange_type='topic', durable = True)
# result = channel.queue_declare(exclusive=True)
# queue_name = result.method.queue

print(' [*] Waiting for logs. To exit press CTRL+C')

def callback(ch, method, properties, body):
    print(" [x] %r" % (body,))

channel.basic_consume(queue_name, callback)
channel.start_consuming()