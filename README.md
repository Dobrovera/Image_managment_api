# Image Management API

Этот проект представляет собой микросервисное приложение для управления изображениями, с разделением на сервисы авторизации и работы с изображениями. Сервис поддерживает такие функции, как загрузка, обновление и удаление изображений, и использует RabbitMQ для отправки событий об изменениях изображений другим сервисам.

## Технологии

- **Python 3.11** + **FastAPI** для создания API
- **PostgreSQL** для хранения данных
- **RabbitMQ** в качестве брокера сообщений
- **Docker** и **Docker Compose** для контейнеризации и управления зависимостями

## Структура проекта

```plaintext
project/
├── apps/
│   ├── libs/
│   │   ├── auth/
│   │   ├── config/
│   │   ├── database/
│   │   └── broker/
│   ├── main_api/
│   └── image_api/
├── docker/
│   ├── MainApi.Dockerfile
│   └── ImageApi.Dockerfile
├── storage/
├── docker-compose.yml
└── README.md
└── requirements.txt
```

•	apps/libs/auth/ — логика авторизации (JWT).

•	apps/libs/config/ — конфигурационные файлы.

•	apps/libs/database/ — модели и подключение к базе данных.

•	apps/libs/broker/ — модуль для отправки сообщений через RabbitMQ.

•	main_api/ — сервис для авторизации.

•	image_api/ — сервис для управления изображениями.

•	docker/ — Dockerfile для обоих сервисов.

•	tests/ — тесты.

# Настройка проекта Image Management API

## Шаг 1: Клонирование репозитория

Сначала клонируйте репозиторий проекта на свою локальную машину:

```bash
git clone <URL вашего репозитория>
cd <название папки с проектом>
```

## Шаг 2: Создание и настройка .env файла

Создайте файл .env в корне проекта и добавьте в него следующие переменные окружения. Эти переменные будут использоваться для настройки подключения к базе данных, JWT-секрету и RabbitMQ.

Пример .env файла:
```
# Database настройки
DATABASE_URL=postgresql://<username>:<password>@db:5432/<dbname>
POSTGRES_USER=<username>
POSTGRES_PASSWORD=<password>
POSTGRES_DB=<dbname>

# JWT секрет для токенов авторизации
JWT_SECRET=<ваш_jwt_секрет>

# RabbitMQ настройки
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_QUEUE=image_events
```

Замените все <значения> на актуальные значения.

## Шаг 3: Запуск проекта
```
docker-compose up --build
```

После выполнения этой команды будут запущены следующие сервисы:

	•	web_app на порту 8000 — сервис авторизации
	•	image_service на порту 8001 — сервис для работы с изображениями
	•	db — PostgreSQL для хранения данных
	•	rabbitmq на портах 5672 и 15672 — брокер сообщений для передачи событий