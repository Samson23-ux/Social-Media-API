import sentry_sdk
from uuid import UUID
from sqlalchemy.orm import Session
from sentry_sdk import logger as sentry_logger

from app.models.users import User, Role
from app.core.exceptions import ServerError
from app.api.v1.schemas.users import UserReadV1
from app.api.v1.schemas.admin import UserCountV1
from app.core.security import validate_refresh_token
from app.api.v1.services.user_service import user_service_v1
from app.api.v1.repositories.admin_repo import admin_repo_v1
from app.core.exceptions import UsersNotFoundError, UserNotFoundError


class AdminServiceV1:
    @staticmethod
    def get_all_active_users(
        admin_user: User, refresh_token: str, db: Session
    ) -> UserCountV1:
        _ = validate_refresh_token(refresh_token, db)

        try:
            role_id: UUID = admin_user.role_id
            users: int = admin_repo_v1.count_users(role_id, db)
            users_count: UserCountV1 = UserCountV1(total=users)
            sentry_logger.info('Total active users retrieved from database')
            return users_count
        except Exception as e:
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                'Internal server error occured while retrieving active users count from database'
            )
            raise ServerError() from e


    @staticmethod
    def get_suspended_users(
        admin_user: User, refresh_token: str, db: Session
    ) -> list[UserReadV1]:
        _ = validate_refresh_token(refresh_token, db)

        try:
            role_id: UUID = admin_user.role_id
            users_db: list[User] = admin_repo_v1.get_suspended_users(role_id, db)

            if not users_db:
                sentry_logger.error('Suspended users not found')
                raise UsersNotFoundError()

            users: list[UserReadV1] = []
            for user in users_db:
                user_read = UserReadV1.model_validate(user)
                users.append(user_read)

            sentry_logger.info('Total suspended users retrieved from database')
            return users
        except Exception as e:
            if isinstance(e, UsersNotFoundError):
                raise UsersNotFoundError()

            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                'Internal server error occured while retrieving suspended users count from database'
            )
            raise ServerError() from e


    @staticmethod
    def assign_admin_role(
        admin_user: User, username: str, refresh_token: str, db: Session
    ) -> UserReadV1:
        _ = validate_refresh_token(refresh_token, db)

        user_db: User = user_service_v1.get_user_by_username(username, db)

        try:
            role: Role = user_service_v1.get_role('admin', db)
            user_db.role_id = role.id

            user_service_v1.add_user(user_db, db)
            db.commit()

            user: UserReadV1 = UserReadV1.model_validate(user_db)
            sentry_logger.info(
                'User {id} role updated to admin by admin {admin_id}',
                id=user.id,
                admin_id=admin_user.id,
            )
            return user
        except Exception as e:
            db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                'Internal server error occured while updating user {id} role', id=user.id
            )
            raise ServerError() from e


    @staticmethod
    def suspend_user(
        admin_user: User, username: str, refresh_token: str, db: Session
    ) -> UserReadV1:
        _ = validate_refresh_token(refresh_token, db)

        user: User = user_service_v1.get_user_by_username(username, db)

        try:
            user.is_suspended = True
            user_service_v1.add_user(user, db)
            db.commit()
            user: UserReadV1 = UserReadV1.model_validate(user)
            sentry_logger.info(
                'User {id} suspended by admin {admin_id}',
                id=user.id,
                admin_id=admin_user.id,
            )
            return user
        except Exception as e:
            db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                'Internal server error occured while suspending user {id}', id=user.id
            )
            raise ServerError() from e


    @staticmethod
    def unsuspend_user(
        admin_user: User, username: str, refresh_token: str, db: Session
    ) -> UserReadV1:
        _ = validate_refresh_token(refresh_token, db)

        role_id = admin_user.role_id
        user_db: User = admin_repo_v1.get_suspended_user(role_id, username, db)

        if not user_db:
                sentry_logger.error('Suspended user not found')
                raise UserNotFoundError()

        try:
            user_db.is_suspended = False
            user_service_v1.add_user(user_db, db)
            db.commit()
            user: UserReadV1 = UserReadV1.model_validate(user_db)
            sentry_logger.info(
                'User {id} unsuspended by admin {admin_id}',
                id=user.id,
                admin_id=admin_user.id,
            )
            return user
        except Exception as e:
            if isinstance(e, UserNotFoundError):
                raise UserNotFoundError()

            db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                'Internal server error occured while unsuspending user {id}', id=user.id
            )
            raise ServerError() from e


admin_service_v1 = AdminServiceV1()
