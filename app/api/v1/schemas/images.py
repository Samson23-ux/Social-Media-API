from typing import Optional
from pydantic import BaseModel, field_validator


class ImageBaseV1(BaseModel):
    image_url: str
    image_type: str
    image_size: int

    @field_validator('image_url', mode='after')
    @classmethod
    def img_url_to_lower(cls, i: str):
        return i.lower()


#Base class for all user response
class BaseResponseV1(BaseModel):
    message: Optional[str]


class ImageInDBV1(ImageBaseV1):
    pass


class ImageReadV1(BaseModel):
    image_url: list[str]


class ImageResponseV1(BaseResponseV1):
    data: ImageReadV1
