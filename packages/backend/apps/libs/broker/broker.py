import pika
import json
import logging

from apps.libs.config.core_config import core_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pika_logger = logging.getLogger('pika')
pika_logger.setLevel(logging.ERROR)


connection = None


def create_connection():
    global connection
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=core_config.rabbitmq_host,
            port=core_config.rabbitmq_port
        ))
        logger.info("RabbitMQ connection established.")
    except pika.exceptions.AMQPConnectionError as e:
        connection = None
        logger.error(f"Failed to connect to RabbitMQ: {e}")


async def send_message(event_type, data):
    create_connection()
    if connection:
        channel = connection.channel()
        channel.queue_declare(queue=core_config.rabbitmq_queue)

        message = json.dumps({'event_type': event_type, 'data': data})
        channel.basic_publish(exchange='', routing_key=core_config.rabbitmq_queue, body=message)
        logger.info(f" [x] Sent '{event_type}', user_id: {data['user_id']}")
    else:
        logger.error("No connection to RabbitMQ. Message not sent.")
