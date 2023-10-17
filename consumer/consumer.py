import pika

def on_message_received(ch, method, properties, body):
    print(f"{body}")

#connection_parameters = pika.ConnectionParameters('localhost')
connection_parameters = pika.ConnectionParameters('rabbitmq3') # instead of localhost, because running from docker container
connection = pika.BlockingConnection(connection_parameters)
channel = connection.channel()

channel.exchange_declare(exchange='notification', exchange_type='fanout')

queue = channel.queue_declare(queue='', exclusive=True)

channel.queue_bind(exchange='notification', queue=queue.method.queue)

channel.basic_consume(queue=queue.method.queue, auto_ack=True,
    on_message_callback=on_message_received)

print("Starting Consuming")

channel.start_consuming()