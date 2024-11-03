FROM python:3.11-alpine

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY packages/backend/ /app

CMD ["python", "-m", "apps.image_service.main"]