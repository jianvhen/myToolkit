import pika
import json
import time

host = "127.0.0.1"
port = 7247
credentials = pika.PlainCredentials('sdp-rabbitmq-api', 'password')
connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port, credentials = credentials))
 
channel = connection.channel()

exchange = "exchange2"
queue = "test-log"
channel.queue_declare(queue=queue, durable = True)
# channel.queue_declare(queue=queue)

for i in range(1000000):
    times = time.time()
    message = json.dumps({'OrderId':"1000%s"%i, 'time': times})
    channel.basic_publish(exchange = exchange, routing_key = 'test', body = message, properties=pika.BasicProperties(delivery_mode=2,))
    # channel.basic_publish(exchange='exchange2', routing_key='hello', body='Hello World!')

print(" [x] Sent 'Hello World!'")
connection.close()