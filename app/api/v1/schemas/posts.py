import enum
from uuid import UUID
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator

from app.core.exceptions import PostVisibilityError


class VisibilityEnum(str, enum.Enum):
    PUBLIC: str = 'public'
    FOLLOWERS: str = 'followers'
    PRIVATE: str = 'private'


# Base class for all user response
class BaseResponseV1(BaseModel):
    message: Optional[str]


class PostBaseV1(BaseModel):
    title: str
    content: str
    visibility: str = VisibilityEnum.PUBLIC


    @field_validator('visibility', mode='after')
    @classmethod
    def get_visibility_enum(cls, v: str):
        visibility = None
        if v.lower() == VisibilityEnum.PUBLIC.value:
            visibility = VisibilityEnum.PUBLIC
        elif v.lower() == VisibilityEnum.FOLLOWERS.value:
            visibility = VisibilityEnum.FOLLOWERS
        elif v.lower() == VisibilityEnum.PRIVATE.value:
            visibility = VisibilityEnum.PRIVATE
        else:
            raise PostVisibilityError()
        return visibility


class CommentBaseV1(BaseModel):
    content: str


class CommentCreateV1(CommentBaseV1):
    pass

    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')


class PostCreateV1(PostBaseV1):
    pass

    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')


class PostUpdateV1(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    visibility: Optional[str] = VisibilityEnum.PUBLIC
    content: Optional[str] = None


class PostReadBaseV1(PostBaseV1):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CommentReadBaseV1(CommentBaseV1):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PostReadV1(PostReadBaseV1):
    display_name: str
    username: str
    likes: int = 0
    comments: int = 0


class CommentReadV1(CommentReadBaseV1):
    display_name: str
    username: str
    likes: int


class PostResponseV1(BaseResponseV1):
    data: Optional[PostReadV1 | list[PostReadV1]] = None


class CommentResponseV1(BaseResponseV1):
    data: Optional[CommentReadV1 | list[CommentReadV1]] = None
