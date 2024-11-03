import pytest
from fastapi.testclient import TestClient
from apps.main_api.main import app as app_auth
from apps.image_api.main import app as app_image
import os

client_auth = TestClient(app_auth)
client_image = TestClient(app_image)


@pytest.fixture
def auth_headers():
    # Уникальное имя пользователя для теста
    unique_username = f"test_user_{os.urandom(4).hex()}"

    # Регистрация пользователя через web_app (auth сервис)
    response = client_auth.post("/auth/register", json={
        "username": unique_username,
        "password": "password123!"
    })

    # Если пользователь уже существует, выполняем логин
    if response.status_code == 400:
        response = client_auth.post("/auth/login", json={
            "username": unique_username,
            "password": "password123!"
        })

    # Проверяем успешность получения токена
    assert response.status_code == 200, f"Ошибка регистрации/логина: {response.json()}"
    token = response.json().get("access_token")

    # Возвращаем заголовок с токеном для авторизации
    return {"Authorization": f"Bearer {token}"}


def test_upload_image(auth_headers):
    unique_image_name = f"test_image_{os.urandom(4).hex()}.png"

    # Создаем тестовый файл изображения
    with open("tests/test_image.png", "wb") as f:
        f.write(
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\nIDAT\x08\xd7c\xf8\x0f\x00\x01\x01\x01\x00\x9d^\x1d\xf7\x00\x00\x00\x00IEND\xaeB`\x82"
        )

    # Загружаем изображение в image_service
    upload_response = client_image.post(
        "/image/upload_image",
        headers=auth_headers,
        files={"image": (unique_image_name, open("tests/test_image.png", "rb"), "image/png")},
    )

    # Проверяем успешность загрузки изображения
    assert upload_response.status_code == 200, f"Ошибка загрузки: {upload_response.json()}"
    data = upload_response.json()
    assert "id" in data
    assert data["title"] == unique_image_name
