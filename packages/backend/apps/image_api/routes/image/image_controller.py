from fastapi import APIRouter, Depends, File, UploadFile, Response, status
from sqlalchemy.orm import Session

from apps.libs.auth.auth_dependencies import get_current_user
from apps.libs.database.database import get_db
from apps.libs.database.models import User
from .image_dto import ImageUpdate, ImageOut

from .image_service import (
    service_get_all_images,
    service_get_image_by_id,
    service_update_image_info,
    service_delete_image,
    save_processed_image
)

image_router = APIRouter(prefix="/image", dependencies=[Depends(get_current_user)])


@image_router.post("/upload_image", response_model=ImageOut)
async def upload_image(
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
        Загружает новое изображение и сохраняет его на сервере.
        Только для авторизованных пользователей.
        Только для изображений

        Параметры:
        - image (UploadFile): Файл изображения для загрузки

        Пример curl-запроса:
        ```
            curl -X POST "http://localhost:8000/images/create_image"
            -H "Authorization: Bearer yourAccessToken"
            -F "image=@path/to/image.jpg"
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
            "updated_at": "2024-11-02T18:10:16.510939",
            "user_id": 1
        }

        OR

        {
            "detail": "Not authenticated"
        }
        ```
    """
    return await save_processed_image(image, db, current_user)


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


@image_router.put("/update/{image_id}", response_model=ImageOut)
async def update_image(image_id: int, image_update: ImageUpdate, db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    """
        Обновляет информацию об изображении.
        Только для авторизованных пользователей.
        Доступно только для юзера который загружал изображение

         Параметры:
        - image_id (int): Идентификатор изображения.
        - body (ImageUpdate): Тело запроса, содержащее обновляемые поля.

        Тело запроса может включать:
        - title: Optional[str] - название изображения
        - resolution: Optional[str] - разрешение изображения
        - size: Optional[int] - размер изображения

        Пример curl-запроса:
        ```
            curl -X PUT "http://localhost:8000/images/{image_id}"
            -H "Authorization: Bearer yourAccessToken"
            -d '{
                    "title":"new_name",
                    "resolution":"1920x1080"
                }'
        ```
        Пример ответа:
        ```
        {
            "title": "new_name.png",
            "resolution": "1920x1080",
            "size": 585527,
            "id": 14,
            "file_path": "storage/20241102181354_new_name.png",
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
    return await service_update_image_info(image_id, image_update, db, current_user)


@image_router.delete("/delete/{image_id}")
async def delete_image(image_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
        Удаляет изображение по image_id.
        Только для авторизованных пользователей.
        Доступно только для юзера который загружал изображение

         Параметры:
        - image_id (int): Идентификатор изображения.

        Пример curl-запроса:
        ```
            curl -X DELETE "http://localhost:8000/images/delete/{image_id}"
            -H "Authorization: Bearer yourAccessToken"
        ```
        Пример ответа:
        ```
        200 OK

        OR

        {
            "detail": "Not authenticated"
        }
        ```
    """
    await service_delete_image(image_id, db, current_user)
    return Response(status_code=status.HTTP_200_OK)
