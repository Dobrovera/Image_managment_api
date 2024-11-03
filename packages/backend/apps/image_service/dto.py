from pydantic import BaseModel
from typing import Optional


class ImageUpdate(BaseModel):
    title: Optional[str] = None
    resolution: Optional[str] = None
    size: Optional[int] = None
