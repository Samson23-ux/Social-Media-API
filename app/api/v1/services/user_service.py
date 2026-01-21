import sentry_sdk
from uuid import UUID
from pathlib import Path
from fastapi import UploadFile
from sqlalchemy.orm import Session
from sentry_sdk import logger as sentry_logger


from app.utils import write_file
from app.core.config import settings
from app.models.users import User, Role
from app.models.auth import RefreshToken
from app.models.images import Image, ProfileImage
from app.api.v1.repositories.user_repo import user_repo_v1
from app.api.v1.schemas.images import ImageInDBV1, ImageReadV1
from app.core.security import validate_refresh_token
from app.api.v1.schemas.users import (
    RoleCreateV1,
    UserUpdateV1,
    UserProfileV1,
    UserReadV1,
)

from app.core.exceptions import (
    ServerError,
    RoleExistsError,
    UserExistsError,
    UserNotFoundError,
    ProfileImageError,
    ProfileImageExistsError,
)


class UserServiceV1:
    @staticmethod
    def get_users(
        db: Session,
        refresh_token: RefreshToken,
        nationality: str | None = None,
        year: int | None = None,
        sort: str | None = None,
        order: str | None = None,
        offset: int = 0,
        limit: int = 10,
    ):
        _ = validate_refresh_token(refresh_token, db)

    @staticmethod
    def get_user_by_id(user_id: UUID, db: Session) -> User:
        user = user_repo_v1.get_user_by_id(user_id, db)
        if not user:
            sentry_logger.error('User with email: {id} not found', id=user_id)
            raise UserNotFoundError()
        return user

    @staticmethod
    def get_user_by_email(email: str, db: Session) -> User:
        user = user_repo_v1.get_user_by_email(email, db)
        if not user:
            sentry_logger.error('User with email: {email} not found', email=email)
            raise UserNotFoundError()
        return user

    @staticmethod
    def get_user_by_username(username: str, db: Session) -> User:
        user = user_repo_v1.get_user_by_username(username, db)
        if not user:
            sentry_logger.error(
                'User with email: {username} not found', username=username
            )
            raise UserNotFoundError()
        return user

    @staticmethod
    def get_user_profile(
        user: User, refresh_token: RefreshToken, db: Session
    ) -> UserProfileV1:
        _ = validate_refresh_token(refresh_token, db)

        user_read = UserReadV1.model_validate(user)
        user_profile = UserProfileV1(**user_read.model_dump(), age=user.age)

        return user_profile

    @staticmethod
    def get_role(role_name: Role, db: Session) -> Role:
        role = user_repo_v1.get_role(role_name, db)
        return role

    @staticmethod
    def add_user(user: User, db: Session):
        user_repo_v1.add_user(user, db)

    @staticmethod
    def create_role(role_create: RoleCreateV1, db: Session) -> Role:
        role = user_repo_v1.get_role(role_create.name, db)

        if role:
            sentry_logger.error('{name} role exists', name=role_create.name)
            raise RoleExistsError()

        role_db = Role(name=role_create.name)

        try:
            user_repo_v1.create_role(role_db, db)
            db.commit()
            sentry_logger.info('{name} role created', name=role_create.name)
        except Exception as e:
            db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                'Internal server error while creating {name} role',
                name=role_create.name,
            )
            raise ServerError() from e
        finally:
            db.close()

        role_out = user_repo_v1.get_role(role_db.name, db)
        return role_out

    @staticmethod
    def update_user(
        user_update: UserUpdateV1, user: User, refresh_token: str, db: Session
    ) -> User:
        _ = validate_refresh_token(refresh_token, db)

        if user_update.email and user_repo_v1.get_user_by_email(user_update.email, db):
            sentry_logger.error(
                'User with email {email} exists', email=user_update.email
            )
            raise UserExistsError()

        if user_update.username and user_repo_v1.get_user_by_username(
            user_update.username, db
        ):
            sentry_logger.error(
                'User with username {username} exists',
                email=user_update.username,
            )
            raise UserExistsError()

        user_update_dict: dict = user_update.model_dump(exclude_unset=True)

        for k, v in user_update_dict.items():
            setattr(user, k, v)

        try:
            user_repo_v1.add_user(user, db)
            sentry_logger.info('User {id} profile updated', id=user.id)
            db.commit()
        except Exception as e:
            db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                'Internal server error occured while updating user {id} profile',
                id=user.id,
            )
            raise ServerError() from e

        return user_repo_v1.get_user_by_id(user.id, db)

    @staticmethod
    async def upload_image(
        refresh_token: RefreshToken,
        user: User,
        image_uploads: list[UploadFile],
        db: Session,
    ) -> ImageReadV1:
        _ = validate_refresh_token(refresh_token, db)

        # restricts a user from uploading 0 or more than 2 images
        if len(image_uploads) < 1 or len(image_uploads) > 2:
            sentry_logger.error(
                'User {id} uploaded zero or more than two images', id=user.id
            )
            raise ProfileImageError()

        user_images: list[ProfileImage] = user_repo_v1.get_user_images(user)

        # checks if the user already uploaded both avatar and header images
        if len(user_images) >= 2:
            sentry_logger.error('User {id} profile images complete', id=user.id)
            raise ProfileImageExistsError()

        for img in image_uploads:
            image_id: UUID = user_repo_v1.get_image_id(img.filename, db)

            # this ensures a duplicate image is not created
            # and the profile image is created directly instead
            # allowing just one type of image on disk and database(images table)
            if image_id:
                profile_img: ProfileImage = ProfileImage(
                    user_id=user.id, image_id=image_id
                )
                try:
                    user_repo_v1.create_profile_image(profile_img, db)
                    db.commit()
                    sentry_logger.info('User {id} profile image created', id=user.id)
                except Exception as e:
                    db.rollback()
                    sentry_sdk.capture_exception(e)
                    sentry_logger.error(
                        'Internal server error while creating user {id} profile image',
                        id=user.id,
                    )
                    raise ServerError() from e
            else:
                path: Path = Path(settings.PROFILE_IMAGE_PATH).resolve()
                file_path: str = f'{str(path)}\\{img.filename}'

                await write_file(file_path, img)
                image_name: str = img.filename
                image_type: str = img.content_type
                image_size: int = img.size
                image: Image = Image(
                    **ImageInDBV1(
                        image_url=image_name,
                        image_type=image_type,
                        image_size=image_size,
                    ).model_dump()
                )
                try:
                    user_repo_v1.create_image(user, image, db)
                    db.commit()
                    sentry_logger.info('User {id} profile image created', id=user.id)
                except Exception as e:
                    db.rollback()
                    sentry_sdk.capture_exception(e)
                    sentry_logger.error(
                        'Internal server error while creating user {id} profile image',
                        id=user.id,
                    )
                    raise ServerError() from e

        profile_images: list[ProfileImage] = user_repo_v1.get_user_images(user)

        image_urls = []
        for i in profile_images:
            image_urls.append(i.image.image_url)

        images: ImageReadV1 = ImageReadV1(image_url=image_urls)
        return images

    @staticmethod
    def delete_user_accounts(db: Session):
        '''deletes user accounts 30 days after deactivation'''
        try:
            user_repo_v1.delete_user(db)
            db.commit()
            sentry_logger.info('User accounts deleted permanently')
        except Exception as e:
            db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                'Internal server error while deleting user accounts permanently'
            )
            raise ServerError() from e
        finally:
            db.close()


user_service_v1 = UserServiceV1()
