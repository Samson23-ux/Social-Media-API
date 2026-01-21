import hashlib
import sentry_sdk
from uuid import uuid4
from jose import jwt, JWTError
from pwdlib import PasswordHash
from sqlalchemy.orm import Session
from pwdlib.hashers.argon2 import Argon2Hasher
from sentry_sdk import logger as sentry_logger
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.models.auth import RefreshToken
from app.core.exceptions import AuthenticationError
from app.api.v1.repositories.auth_repo import auth_repo_v1
from app.api.v1.schemas.auth import TokenDataV1, TokenStatus

# Argon2id for hashing password with default parameters
pwhs = PasswordHash(hashers=[Argon2Hasher()])


def hash_password(password: str) -> str:
    password_pepper: str = password + settings.ARGON2_PEPPER
    return pwhs.hash(password_pepper)


def hash_token(token: str) -> str:
    token_byte: bytes = token.encode('utf-8')
    return hashlib.sha256(token_byte).hexdigest()


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


def decode_token(token: str, key: str) -> dict | None:
    try:
        payload: dict = jwt.decode(
            token=token,
            key=key,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError as e:
        sentry_sdk.capture_exception(e)
        return None


def validate_refresh_token(refresh_token: str, db: Session) -> RefreshToken:
    token: dict | None = decode_token(refresh_token, settings.REFRESH_TOKEN_SECRET_KEY)

    # raise authentication error if refresh token has expired
    if not token:
        sentry_logger.error('Error authenticating user. Refresh token not valid')
        raise AuthenticationError()

    refresh_token_db: RefreshToken = auth_repo_v1.get_refresh_token(
        token.get('jti'), db
    )

    if (
        refresh_token_db.status == TokenStatus.REVOKED
        or refresh_token_db.status == TokenStatus.USED
    ):
        sentry_logger.error(
            'Error authenticating user. Refresh token {id} not valid',
            id=refresh_token_db.id,
        )
        raise AuthenticationError()

    return refresh_token_db
