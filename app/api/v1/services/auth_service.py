from uuid import UUID
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta


from app.models.users import User
from app.core.config import settings
from app.models.auth import RefreshToken
from app.api.v1.schemas.auth import RefreshTokenV1
from app.api.v1.repositories.auth_repo import auth_repo_v1
from app.api.v1.repositories.user_repo import user_repo_v1
from app.api.v1.services.user_service import user_service_v1
from app.api.v1.schemas.users import UserCreateV1, UserInDBV1
from app.api.v1.schemas.auth import TokenV1, TokenDataV1, TokenStatus
from app.core.exceptions import (
    CredentialError,
    UserExistsError,
    AuthenticationError,
    PasswordError,
    ServerError,
    UserNotFoundError,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
    hash_password,
)


class AuthServiceV1:
    @staticmethod
    def prepare_tokens(user_id: UUID, username: str) -> dict:
        token_data = TokenDataV1(id=user_id, name=username)
        access_token = create_access_token(token_data)
        token = TokenV1(access_token=access_token)

        refresh_token, token_id, token_exp = create_refresh_token(token_data)
        token_create = RefreshToken(
            **RefreshTokenV1(
                token=refresh_token, user_id=user_id, expires_at=token_exp
            ).model_dump(),
            id=token_id
        )

        data = {
            'access_token': token,
            'token_create': token_create,
            'refresh_token_id': token_id,
        }
        return data

    @staticmethod
    def revoke_refresh_token(refresh_token: RefreshToken):
        refresh_token.status = TokenStatus.REVOKED
        refresh_token.revoked_at = datetime.now(timezone.utc)
        return refresh_token

    @staticmethod
    def sign_up(user_create: UserCreateV1, db: Session) -> User:
        user_with_email = user_repo_v1.get_user_by_email(user_create.email, db)

        if user_with_email:
            raise UserExistsError()

        user_with_username = user_repo_v1.get_user_by_username(user_create.username, db)

        if user_with_username:
            raise UserExistsError()

        user_create.password = hash_password(user_create.password)

        user_in_db = UserInDBV1(**user_create.model_dump())
        role = user_service_v1.get_role(user_in_db.role, db)

        user = User(
            **user_in_db.model_dump(exclude={'role', 'password'}),
            role_id=role.id,
            hash_password=user_create.password
        )

        try:
            user_service_v1.add_user(user, db)
            db.commit()
        except Exception as e:
            db.rollback()
            raise ServerError() from e

        user_out = user_service_v1.get_user_by_id(user.id, db)

        return user_out

    @staticmethod
    def sign_in(email: str, password: str, db: Session):
        user_db = user_service_v1.get_user_by_email(email, db)

        if not user_db:
            raise CredentialError()

        if not verify_password(password, user_db.hash_password):
            raise CredentialError()

        data = AuthServiceV1.prepare_tokens(user_db.id, user_db.username)
        access_token = data.get('access_token')

        refresh_tokens = user_db.refresh_tokens

        # Revoke user's current valid refresh tokens before creating a new on on sign in
        if refresh_tokens:
            for rt in refresh_tokens:
                if rt.status == TokenStatus.VALID:
                    rt.status = TokenStatus.REVOKED

                    try:
                        auth_repo_v1.store_refresh_token(rt, db)
                        db.commit()
                    except Exception as e:
                        db.rollback()
                        raise ServerError() from e

        try:
            auth_repo_v1.store_refresh_token(data.get('token_create'), db)
            db.commit()
        except Exception as e:
            db.rollback()
            raise ServerError() from e

        refresh_token_db = auth_repo_v1.get_refresh_token(
            data.get('refresh_token_id'), db
        ).token

        return access_token, refresh_token_db

    @staticmethod
    def create_access_token(refresh_token: str, db: Session):
        token = decode_token(refresh_token, settings.REFRESH_TOKEN_SECRET_KEY)

        if not refresh_token or not token:
            raise AuthenticationError()

        token_db = auth_repo_v1.get_refresh_token(token.get('jti'), db)

        if token_db:
            if (
                token_db.status == TokenStatus.REVOKED
                or token_db.status == TokenStatus.USED
            ):
                raise AuthenticationError()

        token_db.status = TokenStatus.USED
        token_db.used_at = datetime.now(timezone.utc)

        try:
            auth_repo_v1.store_refresh_token(token_db, db)
            db.commit()
        except Exception as e:
            db.rollback()
            raise ServerError() from e

        user_db = token_db.user

        data = AuthServiceV1.prepare_tokens(user_db.id, user_db.username)
        access_token = data.get('access_token')

        try:
            auth_repo_v1.store_refresh_token(data.get('token_create'), db)
            db.commit()
        except Exception as e:
            db.rollback()
            raise ServerError() from e

        refresh_token_db = auth_repo_v1.get_refresh_token(
            data.get('refresh_token_id'), db
        ).token

        return access_token, refresh_token_db

    @staticmethod
    def sign_out(refresh_token: str, db: Session):
        token = decode_token(refresh_token, settings.REFRESH_TOKEN_SECRET_KEY)

        refresh_token_db = auth_repo_v1.get_refresh_token(token.get('jti'), db)

        if (
            refresh_token_db.status == TokenStatus.REVOKED
            or refresh_token_db.status == TokenStatus.USED
        ):
            raise AuthenticationError()
        else:
            refresh_token_db = AuthServiceV1.revoke_refresh_token(refresh_token_db)

        try:
            auth_repo_v1.store_refresh_token(refresh_token_db, db)
            db.commit()
        except Exception as e:
            db.rollback()
            raise ServerError() from e

    @staticmethod
    def update_password(
        refresh_token: str,
        curr_password: str,
        new_password: str,
        user: User,
        db: Session,
    ):
        if not verify_password(curr_password, user.hash_password):
            raise PasswordError()

        token = decode_token(refresh_token, settings.REFRESH_TOKEN_SECRET_KEY)
        refresh_token_db = auth_repo_v1.get_refresh_token(token.get('jti'), db)

        if (
            refresh_token_db.status == TokenStatus.REVOKED
            or refresh_token_db.status == TokenStatus.USED
        ):
            raise AuthenticationError()
        else:
            token_db = AuthServiceV1.revoke_refresh_token(refresh_token_db)

        try:
            auth_repo_v1.store_refresh_token(token_db, db)
            db.commit()
        except Exception as e:
            db.rollback()
            raise ServerError() from e

        user.hash_password = hash_password(new_password)

        try:
            user_service_v1.add_user(user, db)
            db.commit()
        except Exception as e:
            db.rollback()
            raise ServerError() from e

        return user

    @staticmethod
    def reset_password(
        email: str,
        new_password: str,
        db: Session,
    ):
        user = user_service_v1.get_user_by_email(email, db)

        user.hash_password = hash_password(new_password)

        try:
            user_service_v1.add_user(user, db)
            db.commit()
        except Exception as e:
            db.rollback()
            raise ServerError() from e

        return user

    @staticmethod
    def restore_account(email: str, account_password, db: Session):
        user = user_repo_v1.get_deleted_users(email, db)

        if not user:
            raise UserNotFoundError()

        if not verify_password(account_password, user.hash_password):
            raise CredentialError()

        user.is_delete = False
        user.deleted_at = None
        user.delete_at = None

        try:
            user_service_v1.add_user(user, db)
            db.commit()
        except Exception as e:
            db.rollback()
            raise ServerError() from e

        return user

    @staticmethod
    def delete_account(refresh_token: str, password: str, user: User, db: Session):
        if not verify_password(password, user.hash_password):
            raise PasswordError()

        token = decode_token(refresh_token, settings.REFRESH_TOKEN_SECRET_KEY)
        refresh_token_db = auth_repo_v1.get_refresh_token(token.get('jti'), db)
        
        if (
            refresh_token_db.status == TokenStatus.REVOKED
            or refresh_token_db.status == TokenStatus.USED
        ):
            raise AuthenticationError()
        else:
            AuthServiceV1.revoke_refresh_token(refresh_token_db)

        try:
            auth_repo_v1.store_refresh_token(refresh_token_db, db)
            db.commit()
        except Exception as e:
            db.rollback()
            raise ServerError() from e

        user.is_delete = True
        user.deleted_at = datetime.now(timezone.utc)
        user.delete_at = datetime.now(timezone.utc) + timedelta(minutes=1)

        try:
            user_service_v1.add_user(user, db)
            db.commit()
        except Exception as e:
            db.rollback()
            raise ServerError() from e

    @staticmethod
    def delete_refresh_tokens(db: Session):
        try:
            auth_repo_v1.delete_tokens(db)
            db.commit()
        except Exception as e:
            db.rollback()
            raise ServerError() from e


auth_service_v1 = AuthServiceV1()
