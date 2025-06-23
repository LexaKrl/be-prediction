import pika
import json
from config import Config


class RabbitMQConsumer:
    def __init__(self, callback):
        self.callback = callback
        credentials = pika.PlainCredentials(
            Config.RABBITMQ_USER, Config.RABBITMQ_PASS
        )
        parameters = pika.ConnectionParameters(
            host=Config.RABBITMQ_HOST,
            port=Config.RABBITMQ_PORT,
            credentials=credentials
        )
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=Config.RABBITMQ_QUEUE, durable=True)
        self.channel.basic_consume(
            queue=Config.RABBITMQ_QUEUE,
            on_message_callback=self._handle_message,
            auto_ack=True
        )

    def _handle_message(self, ch, method, properties, body):
        try:
            message = json.loads(body)
            user_id = message.get('user_id')
            if user_id:
                self.callback(user_id)
        except json.JSONDecodeError:
            print("Ошибка декодирования сообщения")

    def start_consuming(self):
        print("Ожидание сообщений...")
        self.channel.start_consuming()

    def close(self):
        self.connection.close()