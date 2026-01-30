from fastapi import Depends
from sqlalchemy.orm import Session
from sentry_sdk import logger as sentry_logger
from fastapi.security import OAuth2PasswordBearer


from app.models.users import User
from app.core.config import settings
from app.core.security import decode_token
from app.api.v1.schemas.users import UserRole
from app.database.session import SessionLocal
from app.api.v1.services.user_service import user_service_v1

from app.core.exceptions import AuthenticationError, AuthorizationError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/auth/sign-in/')


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    payload: dict = decode_token(token, settings.ACCESS_TOKEN_SECRET_KEY)

    if not payload:
        sentry_logger.error('Error authenticating user')
        raise AuthenticationError()

    user = user_service_v1.get_user_by_id(payload.get('sub'), db)
    return user


def required_roles(roles: list[UserRole]):
    def role_checker(user: User = Depends(get_current_user)):
        if user.role.name not in roles:
            sentry_logger.error('User not permitted')
            raise AuthorizationError()
        return user

    return role_checker
