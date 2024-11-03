FROM python:3.11-alpine

# Установка рабочей директории
WORKDIR /app

# Копируем зависимости
COPY requirements.txt /app/

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все необходимые каталоги
COPY packages/backend/ /app/

# Обновляем PYTHONPATH, чтобы Python знал, где искать модули
ENV PYTHONPATH="/app/packages/backend:${PYTHONPATH}"

# Запускаем тесты и сервер
CMD ["sh", "-c", "pytest /app/tests/ && uvicorn apps.main_api.main:app --host 0.0.0.0 --port 8000"]