import os
import shutil
from datetime import datetime

from sqlalchemy.orm import Session
from PIL import Image as PILImage
from fastapi import HTTPException, UploadFile

from apps.libs.broker.broker import send_message
from apps.libs.database.models import Image, User
from apps.image_api.routes.image.image_dto import ImageUpdate


async def save_processed_image(image: UploadFile, db: Session, current_user) -> Image:
    # Директория для хранения изображений
    default_size = (500, 500)

    directory = "storage"
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Путь для сохранения обработанного изображения
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    processed_path = os.path.join(directory, f"{timestamp}_{image.filename}")

    # Проверяем, что файл является изображением
    try:
        with PILImage.open(image.file) as img:
            img_format = img.format  # Получаем формат изображения (например, JPEG, PNG)

            # Изменяем размер и преобразуем изображение в оттенки серого
            img_resized = img.resize(default_size).convert("L")
            img_resized.save(processed_path, format=img_format)  # Сохраняем изображение на диск

            # Получаем окончательный размер файла и разрешение
            final_width, final_height = img_resized.size
            image_size = os.path.getsize(processed_path)
    except (IOError, SyntaxError) as e:
        raise HTTPException(status_code=400, detail="Invalid image file")

    # Создаем запись об обработанном изображении в БД
    db_image = Image(
        title=image.filename,
        file_path=processed_path,
        resolution=f"{final_width}x{final_height}",
        size=image_size,
        user_id=current_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)

    send_message("UPLOAD", db_image.id)

    return db_image


async def service_get_all_images(db):
    images = db.query(Image).all()
    return images


async def service_get_image_by_id(image_id: int, db: Session):
    image = db.query(Image).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return image


async def service_update_image_info(
        image_id: int,
        image_update: ImageUpdate,
        db: Session,
        current_user: User
):
    image = db.query(Image).filter(Image.id == image_id, Image.user_id == current_user.id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    image_data = image_update.dict(exclude_unset=True)
    for key, value in image_data.items():
        setattr(image, key, value)
    db.commit()

    send_message("UPDATE", image.id)

    return image


async def service_delete_image(
        image_id: int,
        db: Session,
        current_user: User
):
    image = db.query(Image).filter(Image.id == image_id, Image.user_id == current_user.id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    db.delete(image)
    db.commit()

    send_message("DELETE", image.id)

    return
