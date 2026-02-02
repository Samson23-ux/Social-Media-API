import sentry_sdk
from uuid import UUID
from sqlalchemy.orm import Session
from sentry_sdk import logger as sentry_logger
from datetime import datetime, timezone, timedelta


from app.models.users import User, Role
from app.models.auth import RefreshToken
from app.api.v1.schemas.auth import RefreshTokenV1
from app.api.v1.repositories.auth_repo import auth_repo_v1
from app.api.v1.repositories.user_repo import user_repo_v1
from app.api.v1.services.user_service import user_service_v1
from app.api.v1.schemas.users import UserCreateV1, UserInDBV1
from app.api.v1.schemas.auth import TokenV1, TokenDataV1, TokenStatus
from app.core.exceptions import (
    ServerError,
    PasswordError,
    UserExistsError,
    CredentialError,
    UserNotFoundError,
)
from app.core.security import (
    hash_token,
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    validate_refresh_token,
)


class AuthServiceV1:
    @staticmethod
    def prepare_tokens(user_id: UUID, username: str) -> dict:
        '''create access and refresh tokens'''
        token_data: TokenDataV1 = TokenDataV1(id=user_id, name=username)
        access_token: str = create_access_token(token_data)
        token: TokenV1 = TokenV1(access_token=access_token)

        refresh_token, token_id, token_exp = create_refresh_token(token_data)
        token_create: RefreshToken = RefreshToken(
            **RefreshTokenV1(
                token=refresh_token, user_id=user_id, expires_at=token_exp
            ).model_dump(),
            id=token_id
        )

        data: dict = {
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
        user_with_email: User | None = user_repo_v1.get_user_by_email(
            user_create.email, db
        )

        if user_with_email:
            sentry_logger.error(
                'User with email {email} exists', email=user_with_email.email
            )
            raise UserExistsError()

        user_with_username: User | None = user_repo_v1.get_user_by_username(
            user_create.username, db
        )

        if user_with_username:
            sentry_logger.error(
                'User with username {username} exists',
                email=user_with_username.username,
            )
            raise UserExistsError()

        user_create.password = hash_password(user_create.password)

        user_in_db: UserInDBV1 = UserInDBV1(**user_create.model_dump())

        role: Role = user_service_v1.get_role(user_in_db.role, db)

        user: User = User(
            **user_in_db.model_dump(exclude={'role', 'password'}),
            role_id=role.id,
            hash_password=user_create.password
        )

        try:
            user_service_v1.add_user(user, db)
            db.commit()
            sentry_logger.info('User {id} created successfully', id=user.id)
        except Exception as e:
            db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error('Internal server error while creating user')
            raise ServerError() from e

        user_out: User = user_service_v1.get_user_by_id(user.id, db)

        return user_out

    @staticmethod
    def sign_in(email: str, password: str, db: Session) -> tuple:
        user_db: User = user_service_v1.get_user_by_email(email, db)
        is_password_correct: bool = verify_password(password, user_db.hash_password)

        if not user_db or not is_password_correct:
            sentry_logger.error('Invalid Credentials while signing in')
            raise CredentialError()

        data = AuthServiceV1.prepare_tokens(user_db.id, user_db.username)
        access_token: str = data.get('access_token')

        refresh_tokens: list[RefreshToken] = user_db.refresh_tokens

        # Revoke user's current valid refresh tokens before creating a new on on sign in
        if refresh_tokens:
            for rt in refresh_tokens:
                if rt.status == TokenStatus.VALID:
                    rt.status = TokenStatus.REVOKED

                    try:
                        auth_repo_v1.store_refresh_token(rt, db)
                        db.commit()
                        sentry_logger.info(
                            'Refresh token {id} status updated', id=rt.id
                        )
                    except Exception as e:
                        db.rollback()
                        sentry_sdk.capture_exception(e)
                        sentry_logger.error(
                            'Internal server error while updating refresh token {id}',
                            id=rt.id,
                        )
                        raise ServerError() from e

        try:
            refresh_token: RefreshToken = data.get('token_create')
            refresh_token_out = refresh_token.token
            refresh_token.token = hash_token(refresh_token.token)
            auth_repo_v1.store_refresh_token(refresh_token, db)
            db.commit()
            sentry_logger.info('Refresh token {id} created', id=refresh_token.id)
        except Exception as e:
            db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                'Internal server error while creating refresh token {id}',
                id=refresh_token.id,
            )
            raise ServerError() from e

        return access_token, refresh_token_out

    @staticmethod
    def create_access_token(refresh_token: str, db: Session) -> tuple:
        # check if refresh token is valid
        refresh_token_db: RefreshToken = validate_refresh_token(refresh_token, db)

        # mark refresh token as used and rotate token
        refresh_token_db.status = TokenStatus.USED
        refresh_token_db.used_at = datetime.now(timezone.utc)

        try:
            auth_repo_v1.store_refresh_token(refresh_token_db, db)
            db.commit()
            sentry_logger.info(
                'Refresh token {id} status updated', id=refresh_token_db.id
            )
        except Exception as e:
            db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                'Internal server error while updating refresh token {id}',
                id=refresh_token_db.id,
            )
            raise ServerError() from e

        user_db: User = refresh_token_db.user

        data: dict = AuthServiceV1.prepare_tokens(user_db.id, user_db.username)
        access_token: str = data.get('access_token')

        try:
            refresh_token: RefreshToken = data.get('token_create')
            refresh_token_out: str = refresh_token.token
            refresh_token.token = hash_token(refresh_token.token)
            auth_repo_v1.store_refresh_token(refresh_token, db)
            db.commit()
            sentry_logger.info('Refresh token {id} created', id=refresh_token.id)
        except Exception as e:
            db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                'Internal server error while creating refresh token {id}',
                id=refresh_token.id,
            )
            raise ServerError() from e

        return access_token, refresh_token_out

    @staticmethod
    def sign_out(refresh_token: str, db: Session):
        # check if refresh token is valid
        refresh_token_db: RefreshToken = validate_refresh_token(refresh_token, db)

        refresh_token_db = AuthServiceV1.revoke_refresh_token(refresh_token_db)

        try:
            auth_repo_v1.store_refresh_token(refresh_token_db, db)
            db.commit()
            sentry_logger.info(
                'Refresh token {id} status updated', id=refresh_token_db.id
            )
        except Exception as e:
            db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                'Internal server error while updating refresh token {id}',
                id=refresh_token_db.id,
            )
            raise ServerError() from e

    @staticmethod
    def update_password(
        refresh_token: str,
        curr_password: str,
        new_password: str,
        user: User,
        db: Session,
    ) -> User:
        # check if refresh token is valid
        refresh_token_db: RefreshToken = validate_refresh_token(refresh_token, db)

        if not verify_password(curr_password, user.hash_password):
            sentry_logger.error('Incorrect password')
            raise PasswordError()

        token_db = AuthServiceV1.revoke_refresh_token(refresh_token_db)

        try:
            auth_repo_v1.store_refresh_token(token_db, db)
            db.commit()
            sentry_logger.info(
                'Refresh token {id} status updated', id=refresh_token_db.id
            )
        except Exception as e:
            db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                'Internal server error while updating refresh token {id}',
                id=refresh_token_db.id,
            )
            raise ServerError() from e

        user.hash_password = hash_password(new_password)

        try:
            user_service_v1.add_user(user, db)
            db.commit()
            sentry_logger.info('User {id} password updated', id=user.id)
        except Exception as e:
            db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                'Internal server error while updating user {id} password', id=user.id
            )
            raise ServerError() from e

        return user

    @staticmethod
    def reset_password(
        email: str,
        new_password: str,
        db: Session,
    ) -> User:
        user = user_service_v1.get_user_by_email(email, db)

        user.hash_password = hash_password(new_password)

        try:
            user_service_v1.add_user(user, db)
            db.commit()
            sentry_logger.info('User {id} password reset completed', id=user.id)
        except Exception as e:
            db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                'Internal server error while resetting user {id} password', id=user.id
            )
            raise ServerError() from e

        return user

    @staticmethod
    def reactivate_account(email: str, account_password, db: Session) -> User:
        user = user_repo_v1.get_deleted_user(email, db)


        if not user:
            sentry_logger.error('User with email: {email} not found', email=email)
            raise UserNotFoundError()

        if not verify_password(account_password, user.hash_password):
            sentry_logger.error(
                'Invalid Credentials while reactivating user {id} account', id=user.id
            )
            raise CredentialError()

        user.is_delete = False
        user.deleted_at = None
        user.delete_at = None

        try:
            user_service_v1.add_user(user, db)
            db.commit()
            sentry_logger.info('User {id} account reactivated', id=user.id)
        except Exception as e:
            db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                'Internal server error reactivating user {id} account', id=user.id
            )
            raise ServerError() from e

        return user

    @staticmethod
    def deactivate_account(refresh_token: str, password: str, user: User, db: Session):
        '''deactivates user account'''
        # check if refresh token is valid
        refresh_token_db: RefreshToken = validate_refresh_token(refresh_token, db)

        if not verify_password(password, user.hash_password):
            sentry_logger.error('Incorrect password')
            raise PasswordError()

        AuthServiceV1.revoke_refresh_token(refresh_token_db)

        try:
            auth_repo_v1.store_refresh_token(refresh_token_db, db)
            db.commit()
            sentry_logger.info(
                'Refresh token {id} status updated', id=refresh_token_db.id
            )
        except Exception as e:
            db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                'Internal server error while updating refresh token {id}',
                id=refresh_token_db.id,
            )
            raise ServerError() from e


        user.is_delete = True
        user.deleted_at = datetime.now(timezone.utc)
        user.delete_at = datetime.now(timezone.utc) + timedelta(days=30)

        try:
            user_service_v1.add_user(user, db)
            db.commit()
            sentry_logger.info('User {id} account deactivated', id=user.id)
        except Exception as e:
            db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                'Internal server error while deactivating user {id} account', id=user.id
            )
            raise ServerError() from e

    @staticmethod
    def delete_user_account(refresh_token: str, password: str, user: User, db: Session):
        '''delete account permanently'''
        refresh_token_db = validate_refresh_token(refresh_token, db)

        if not verify_password(password, user.hash_password):
            sentry_logger.error('Incorrect password')
            raise PasswordError()

        AuthServiceV1.revoke_refresh_token(refresh_token_db)

        try:
            auth_repo_v1.store_refresh_token(refresh_token_db, db)
            db.commit()
            sentry_logger.info(
                'Refresh token {id} status updated', id=refresh_token_db.id
            )
        except Exception as e:
            db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                'Internal server error while updating refresh token {id}',
                id=refresh_token_db.id,
            )
            raise ServerError() from e

        try:
            user_repo_v1.delete_user_account(user, db)
            db.commit()
            sentry_logger.info('User {id} account deleted permanently', id=user.id)
        except Exception as e:
            db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                'Internal server error while deleting user {id} account', id=user.id
            )
            raise ServerError() from e

    @staticmethod
    def delete_refresh_tokens(db: Session):
        try:
            auth_repo_v1.delete_tokens(db)
            db.commit()
            sentry_logger.info('Refresh tokens deleted')
        except Exception as e:
            db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error('Internal server error while deleting refresh tokens')
            raise ServerError() from e


auth_service_v1 = AuthServiceV1()
