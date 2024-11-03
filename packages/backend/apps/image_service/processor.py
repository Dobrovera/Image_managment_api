import base64
import os
import pika
import json
import tempfile
import time
import logging

from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile

from apps.image_service.db import (
    save_processed_image,
    service_update_image_info,
    service_delete_image
)
from apps.image_service.dto import ImageUpdate
from apps.libs.database.database import get_db
from apps.libs.config.core_config import core_config
from apps.libs.database.models import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Функция для ожидания подключения к RabbitMQ
def wait_for_rabbitmq_connection(host, port):
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port))
            connection.close()
            break
        except pika.exceptions.AMQPConnectionError:
            time.sleep(5)

# Функция обратного вызова для обработки сообщений
def callback(ch, method, properties, body):
    process_image_action(body)

# Основная функция для запуска слушателя
def start_image_listener():
    wait_for_rabbitmq_connection(core_config.rabbitmq_host, core_config.rabbitmq_port)

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=core_config.rabbitmq_host, port=core_config.rabbitmq_port)
    )
    channel = connection.channel()
    channel.queue_declare(queue=core_config.rabbitmq_queue)

    channel.basic_consume(queue=core_config.rabbitmq_queue, on_message_callback=callback, auto_ack=True)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        connection.close()

# Функция для обработки действий с изображениями
def process_image_action(body):
    data = json.loads(body)
    event_type = data['event_type']

    db: Session = next(get_db())
    user_id = data['data'].get('user_id')
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        logger.error("User not found: %s", user_id)
        return

    try:
        if event_type == 'UPLOAD':
            handle_upload_event(data['data'], user, db)

        elif event_type == 'UPDATE':
            handle_update_event(data['data'], db, user)

        elif event_type == 'DELETE':
            handle_delete_event(data['data'], db, user)

    except HTTPException as e:
        logger.error(f"HTTPException occurred: {e.detail}")
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")


def handle_upload_event(image_data, user, db):
    logger.info("Processing UPLOAD image")

    try:
        if image_data['file_data'].startswith("data:image/png;base64,"):
            image_data['file_data'] = image_data['file_data'][len("data:image/png;base64,"):]
        image_bytes = base64.b64decode(image_data['file_data'])
    except Exception as e:
        logger.error(f"Error decoding image: {e}")
        return

    temp_file_path = save_image_to_temp_file(image_bytes)

    try:
        with open(temp_file_path, 'rb') as img_file:
            upload_file = UploadFile(file=img_file, filename=image_data['title'])
            save_processed_image(upload_file, db, user)
            logger.info("Image processed and saved for user_id: %s", user.id)
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            logger.info("Temporary file removed: %s", temp_file_path)


def handle_update_event(update_data, db, user):
    logger.info("Processing UPDATE event")
    image_id = update_data['image_id']
    image_update = ImageUpdate(**update_data['new_data'])

    updated_image = service_update_image_info(image_id, image_update, db, user)  # Здесь убрано await
    logger.info("Image updated: %s", updated_image.id)


def handle_delete_event(delete_data, db, user):
    logger.info("Processing DELETE event")
    image_id = delete_data['image_id']
    service_delete_image(image_id, db, user)
    logger.info("Image deleted: %s", image_id)


def save_image_to_temp_file(image_bytes):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
        temp_file.write(image_bytes)
        return temp_file.name
