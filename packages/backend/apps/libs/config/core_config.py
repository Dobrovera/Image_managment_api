import os

from pydantic_settings import BaseSettings


class CoreConfig(BaseSettings):
    # Параметры для основного API и API изображений
    port_main_api: int = int(os.getenv("PORT_MAIN_API", 8000))
    port_image_api: int = int(os.getenv("PORT_IMAGE_API", 8001))

    # Параметры базы данных
    database_url: str = os.getenv("DATABASE_URL")

    # Параметры JWT
    jwt_secret: str = os.getenv("JWT_SECRET", "your_jwt_secret")
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 30

    # Параметры RabbitMQ
    rabbitmq_host: str = os.getenv("RABBITMQ_HOST", "rabbitmq")
    rabbitmq_port: int = int(os.getenv("RABBITMQ_PORT", 5672))
    rabbitmq_queue: str = os.getenv("RABBITMQ_QUEUE", "image_events")


core_config = CoreConfig()
