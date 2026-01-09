from uuid import UUID
from pydantic import BaseModel


# User claims to be signed
class TokenDataV1(BaseModel):
    id: UUID
    name: str


# Token model to be returned
class TokenV1(BaseModel):
    access_token: str
    token_type: str


class LoginOutV1(BaseModel):
    message: str
    data: TokenV1
