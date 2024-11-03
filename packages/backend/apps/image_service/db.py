import os
import logging

from datetime import datetime
from PIL import Image as PILImage
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from apps.image_service.dto import ImageUpdate
from apps.libs.database.models import Image, User


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def service_update_image_info(
        image_id: int,
        image_update: ImageUpdate,
        db: Session,
        current_user: User
):
    image = db.query(Image).filter_by(id=image_id, user_id=current_user.id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    image_data = image_update.dict(exclude_unset=True)
    for key, value in image_data.items():
        setattr(image, key, value)
    db.commit()

    return image


def service_delete_image(
        image_id: int,
        db: Session,
        current_user: User
):
    image = db.query(Image).filter_by(id=image_id, user_id=current_user.id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    db.delete(image)
    db.commit()

    return


def save_processed_image(image: UploadFile, db: Session, current_user) -> Image:
    default_size = (500, 500)

    directory = "storage"
    if not os.path.exists(directory):
        os.makedirs(directory)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    processed_path = os.path.join(directory, f"{timestamp}_{image.filename}")

    try:
        with PILImage.open(image.file) as img:
            img_format = img.format

            img_resized = img.resize(default_size).convert("L")
            img_resized.save(processed_path, format=img_format)

            final_width, final_height = img_resized.size
            image_size = os.path.getsize(processed_path)
    except (IOError, SyntaxError) as e:
        raise HTTPException(status_code=400, detail="Invalid image file")

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
    logger.info("Save processed image to database")

    return db_image
