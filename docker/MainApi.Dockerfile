# Используем официальный образ Python
FROM python:3.11-alpine

# Установка рабочей директории
WORKDIR /app

# Скопируйте зависимости
COPY requirements.txt /app/

# Установите зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем только папку main_api и нужные зависимости из libs
COPY packages/backend/ /app

# Запускаем сервер
CMD ["uvicorn", "apps.main_api.main:app", "--host", "0.0.0.0", "--port", "8000"]