import re
import enum
from typing import Optional, Any
from datetime import date, datetime
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict


from app.core.exceptions import UsernameError

class UserRole(str, enum.Enum):
    USER: str = 'user'
    ADMIN: str = 'admin'


class UserBaseV1(BaseModel):
    display_name: str
    username: str = Field(
        min_length=6,
        max_length=20,
        description='Unique username with @ e.g -> @example_user',
    )
    email: EmailStr
    dob: date
    nationality: str
    bio: str = Field(max_length=35)

    @field_validator('email', mode='after')
    @classmethod
    def email_to_lower(cls, e: EmailStr):
        return e.lower()

    @field_validator('username', mode='after')
    @classmethod
    def validate_username(cls, u: str):
        regex_text = re.compile(r'^@(\w+){5}[^@]$')
        m = regex_text.search(u)

        if not m:
            raise UsernameError()
        return m.group()


# Base class for all user response
class BaseResponseV1(BaseModel):
    message: Optional[str]


class UserCreateV1(UserBaseV1):
    password: str = Field(min_length=8)

    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')


class UserInDBV1(UserCreateV1):
    role: str = UserRole.USER
    is_delete: bool = False
    created_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    delete_at: Optional[datetime] = None


class UserUpdateV1(BaseModel):
    display_name: Optional[str] = None
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    dob: Optional[date] = None
    nationality: Optional[str] = None
    bio: Optional[str] = None

    @field_validator('email', mode='after')
    @classmethod
    def email_to_lower(cls, e: Any):
        if isinstance(e, EmailStr):
            return e.lower()

    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')


class UserReadV1(UserBaseV1):
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RoleInDBV1(BaseModel):
    name: UserRole


class RoleCreateV1(RoleInDBV1):
    pass


class UserResponseV1(BaseResponseV1):
    data: Optional[UserReadV1 | list[UserReadV1]] = None


class RoleResponseV1(BaseResponseV1):
    data: Optional[RoleInDBV1 | list[RoleInDBV1]] = None
