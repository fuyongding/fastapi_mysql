import pika
from pika.exchange_type import ExchangeType

class RabbitMQService:
    def __init__(self, rabbitmq_url: str):
        self.rabbitmq_url = rabbitmq_url

    def connect(self) -> None:
        self.connection_parameters = pika.ConnectionParameters(self.rabbitmq_url)
        self.connection = pika.BlockingConnection(self.connection_parameters)
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='notification', exchange_type=ExchangeType.fanout)

    def publish(self, message: str):
        self.channel.basic_publish(
            exchange='notification',
            routing_key='',
            body=message
        )

    def close(self):
        self.connection.close()

#rabbitmq_service: RabbitMQService = RabbitMQService('localhost')