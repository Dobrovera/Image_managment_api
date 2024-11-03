import base64
from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile

from apps.image_service.dto import ImageUpdate
from apps.libs.broker.broker import send_message
from apps.libs.database.models import Image, User


async def service_upload_image(
        image: UploadFile,
        current_user: User
):
    image_bytes = await image.read()
    encoded_image = base64.b64encode(image_bytes).decode('utf-8')

    await send_message("UPLOAD", {
        "title": image.filename,
        "resolution": "1920x1080",
        "size": len(image_bytes),
        "user_id": current_user.id,
        "file_data": encoded_image
    })

    return {"detail": "Image upload request sent to the processing service"}


async def service_update_image(
        image_id: int,
        image_update: ImageUpdate,
        current_user: User
):
    await send_message("UPDATE", {
        "image_id": image_id,
        "new_data": image_update.dict(exclude_unset=True),
        "user_id": current_user.id
    })
    return {"detail": "Image update request sent to the processing service"}


async def service_delete_image(
        image_id: int,
        current_user: User
):
    await send_message("DELETE", {
        "image_id": image_id,
        "user_id": current_user.id
    })
    return {"detail": "Image deletion request sent to the processing service"}


async def service_get_all_images(db):
    images = db.query(Image).all()
    return images


async def service_get_image_by_id(image_id: int, db: Session):
    image = db.query(Image).filter_by(id=image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return image
