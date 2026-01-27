from typing import Optional
from pydantic import BaseModel

# Base class for all user response
class BaseResponseV1(BaseModel):
    message: Optional[str]


class UserCountV1(BaseModel):
    total: int

class UserCountResponse(BaseResponseV1):
    data: UserCountV1
