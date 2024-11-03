import os
import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from PIL import Image
from apps.main_api.main import app
from apps.libs.database.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_image_api.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module", autouse=True)
def create_test_image():
    image = Image.new("RGB", (100, 100), color="red")
    image.save("tests/test_image.png")

    yield

    os.remove("tests/test_image.png")
