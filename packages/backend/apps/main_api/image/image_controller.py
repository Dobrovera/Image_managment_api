from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File
)
from sqlalchemy.orm import Session

from apps.libs.auth.auth_dependencies import get_current_user
from apps.libs.database.database import get_db
from apps.libs.database.models import User
from .image_dto import ImageUpdate, ImageOut
from .image_service import (
    service_get_all_images,
    service_get_image_by_id,
    service_upload_image,
    service_update_image,
    service_delete_image,
)


image_router = APIRouter(prefix="/image", dependencies=[Depends(get_current_user)])


@image_router.post("/upload_image", response_model=dict)
async def upload_image(
    image: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Загружает новое изображение и отправляет его на обработку.
    Только для авторизованных пользователей.

    Пример запроса:
    ```
    curl -X POST "http://localhost:8000/image/upload_image"
        -H "Authorization: Bearer yourAccessToken"
        -F "image=@path_to_your_image_file"
    ```

    Пример ответа:
    ```
    {
        "detail": "Image upload request sent to the processing service"
    }
    ```

    OR

    {
        "detail": "Not authenticated"
    }
    """
    return await service_upload_image(image, current_user)


@image_router.put("/update/{image_id}", response_model=dict)
async def update_image(
        image_id: int,
        image_update: ImageUpdate,
        current_user: User = Depends(get_current_user)):
    """
    Обновляет информацию об изображении по его идентификатору.
    Только для авторизованных пользователей.

    Пример запроса:
    ```
    curl -X PUT "http://localhost:8000/image/update/{image_id}"
        -H "Authorization: Bearer yourAccessToken"
        -H "Content-Type: application/json"
        -d '{"title": "new_title.png", "resolution": "1920x1080"}'
    ```

    Пример ответа:
    ```
    {
        "detail": "Image update request sent to the processing service"
    }
    ```

    OR

    {
        "detail": "Not authenticated"
    }
    """
    return await service_update_image(image_id, image_update, current_user)


@image_router.delete("/delete/{image_id}", response_model=dict)
async def delete_image(
        image_id: int,
        current_user: User = Depends(get_current_user)):
    """
    Удаляет изображение по его идентификатору.
    Только для авторизованных пользователей.

    Пример запроса:
    ```
    curl -X DELETE "http://localhost:8000/image/delete/{image_id}"
        -H "Authorization: Bearer yourAccessToken"
    ```

    Пример ответа:
    ```
    {
        "detail": "Image deletion request sent to the processing service"
    }
    ```

    OR

    {
        "detail": "Not authenticated"
    }
    """
    return await service_delete_image(image_id, current_user)


@image_router.get("/get_all_images", response_model=list[ImageOut])
async def read_images(db: Session = Depends(get_db)):
    """
    Выдает все изображения.
    Только для авторизованных пользователей

    Пример curl-запроса:
    ```
        curl -X GET "http://localhost:8000/images/get_all_images"
        -H "Authorization: Bearer yourAccessToken"
    ```

    Пример ответа:
    ```
    [
        {
            "title": "name1.png",
            "resolution": "1000x764",
            "size": 585527,
            "id": 10,
            "file_path": "storage/20241102181015_name1.png",
            "created_at": "2024-11-02T18:10:16.510939",
            "updated_at": "2024-11-02T18:10:16.510939",
            "user_id": 1
        },
        {
            "title": "name2.png",
            "resolution": "1000x764",
            "size": 585527,
            "id": 11,
            "file_path": "storage/20241102181015_name2.png",
            "created_at": "2024-11-02T18:10:16.510939",
            "updated_at": "2024-11-02T18:10:16.510939",
            "user_id": 1
        }, ...
    ]

    OR

    {
        "detail": "Not authenticated"
    }
    ```
    """
    return await service_get_all_images(db)


@image_router.get("/{image_id}", response_model=ImageOut)
async def read_image(image_id: int, db: Session = Depends(get_db)):
    """
    Выдает изображение по image_id.
    Только для авторизованных пользователей

    Пример curl-запроса:
    ```
        curl -X GET "http://localhost:8000/images/{image_id}"
        -H "Authorization: Bearer yourAccessToken"
    ```

    Пример ответа:
    ```
    {
        "title": "name.png",
        "resolution": "1000x764",
        "size": 585527,
        "id": 14,
        "file_path": "storage/20241102181354_name.png",
        "created_at": "2024-11-02T18:10:16.510939",
        "updated_at": "2024-11-02T18:10:16.510939"
        "user_id": 1
    }

    OR

    {
        "detail": "Not authenticated"
    }
    ```
    """
    return await service_get_image_by_id(image_id, db)
