import pika

from apps.libs.config.core_config import core_config


def send_message(event_type, image_id):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=core_config.rabbitmq_host,
            port=core_config.rabbitmq_port
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue=core_config.rabbitmq_queue)

    message = f"{event_type},{image_id}"
    channel.basic_publish(exchange='', routing_key=core_config.rabbitmq_queue, body=message)
    print(f" [x] Sent '{message}'")
    connection.close()
