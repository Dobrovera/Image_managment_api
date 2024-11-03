import json
import pytest

from fastapi.testclient import TestClient
from io import BytesIO
from PIL import Image

from apps.libs.database.database import SessionLocal
from apps.main_api.main import app
from unittest.mock import patch


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


@pytest.fixture
def db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def create_test_image():
    image = Image.new('RGB', (100, 100), color='red')
    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr


def test_upload_image(client, db, create_test_image):
    register_data = {
        "username": "testuser",
        "password": "testpassword!"
    }
    client.post("/auth/register", json=register_data)

    login_data = {
        "username": "testuser",
        "password": "testpassword!"
    }
    response = client.post("/auth/login", json=login_data)
    token = response.json().get("access_token")

    response = client.post(
        "/image/upload_image",
        headers={"Authorization": f"Bearer {token}"},
        files={"image": ("test_image.png", create_test_image, "image/png")}
    )

    assert response.status_code == 200
    assert response.json() == {"detail": "Image upload request sent to the processing service"}


def test_get_all_images(client, db):
    register_data = {
        "username": "testuser",
        "password": "testpassword!"
    }
    client.post("/auth/register", json=register_data)

    login_data = {
        "username": "testuser",
        "password": "testpassword!"
    }
    response = client.post("/auth/login", json=login_data)
    token = response.json().get("access_token")

    response = client.get(
        "/image/get_all_images",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_image_service_listener(client):
    with patch('apps.image_service.processor.process_image_action') as mock_process_image_action:
        mock_process_image_action.return_value = None  # Заменяем реальную обработку на заглушку

        body = json.dumps({
            'event_type': 'UPLOAD',
            'data': {
                'user_id': 1,
                'file_data': 'data:image/png;base64,example_base64_string',
                'title': 'test_image.png',
            }
        })

        mock_process_image_action(body)
        mock_process_image_action.assert_called_once_with(body)
