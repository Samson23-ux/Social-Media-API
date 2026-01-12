import enum
from uuid import UUID
from typing import Optional
from datetime import datetime
from pydantic import BaseModel

#Base class for all auth response
class BaseResponseV1(BaseModel):
    message: Optional[str]

class TokenStatus(str, enum.Enum):
    VALID: str = 'valid'
    REVOKED: str = 'revoked'
    USED: str = 'used'


# User claims to be signed
class TokenDataV1(BaseModel):
    id: UUID
    name: str


# Token model to be returned
class TokenV1(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class RefreshTokenV1(BaseModel):
    token: str
    user_id: UUID
    status: Optional[TokenStatus] = None
    created_at: Optional[datetime] = None
    expires_at: datetime
    used_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None
