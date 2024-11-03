from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ImageBase(BaseModel):
    title: str
    resolution: str
    size: int


class ImageCreate(ImageBase):
    pass


class ImageUpdate(BaseModel):
    title: Optional[str] = None
    resolution: Optional[str] = None
    size: Optional[int] = None


class ImageOut(ImageBase):
    id: int
    file_path: str
    created_at: datetime
    updated_at: datetime
    user_id: int

    class Config:
        orm_mode = True
