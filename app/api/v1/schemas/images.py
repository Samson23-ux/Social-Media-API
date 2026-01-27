from typing import Optional
from pydantic import BaseModel


#Base class for all user response
class BaseResponseV1(BaseModel):
    message: Optional[str]


class ImageReadV1(BaseModel):
    image_url: list[str]


class ImageResponseV1(BaseResponseV1):
    data: ImageReadV1
