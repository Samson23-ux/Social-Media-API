from uuid import uuid4
from jose import jwt, JWTError
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.api.v1.schemas.auth import TokenDataV1

# Argon2id for hashing password with default parameters
pwhs = PasswordHash(hashers=[Argon2Hasher()])


def hash_password(password: str) -> str:
    password_pepper: str = password + settings.ARGON2_PEPPER
    return pwhs.hash(password_pepper)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_pepper: str = plain_password + settings.ARGON2_PEPPER
    return pwhs.verify(password_pepper, hashed_password)


def create_access_token(data: TokenDataV1, expire_time: timedelta | None = None) -> str:
    if expire_time:
        expiry_time: datetime = datetime.now(timezone.utc) + expire_time
    else:
        expiry_time: datetime = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_TIME
        )

    payload: dict = {
        'sub': str(data.id),
        'name': data.name,
        'exp': expiry_time,
        'iat': datetime.now(timezone.utc),
    }

    token: str = jwt.encode(
        claims=payload,
        key=settings.ACCESS_TOKEN_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return token


def create_refresh_token(
    data: TokenDataV1, expire_time: timedelta | None = None
) -> tuple:
    if expire_time:
        expiry_time: datetime = datetime.now(timezone.utc) + expire_time
    else:
        expiry_time: datetime = datetime.now(timezone.utc) + timedelta(
            minutes=settings.REFRESH_TOKEN_EXPIRE_TIME
        )

    payload: dict = {
        'sub': str(data.id),
        'name': data.name,
        'exp': expiry_time,
        'iat': datetime.now(timezone.utc),
        'jti': str(uuid4()),
    }

    token: str = jwt.encode(
        claims=payload,
        key=settings.REFRESH_TOKEN_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return token, payload.get('jti'), payload.get('exp')


def decode_token(token: str, key: str):
    try:
        payload: dict = jwt.decode(
            token=token,
            key=key,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError:
        return None
