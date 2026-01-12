from uuid import UUID
from pathlib import Path
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.utils import write_file
from app.core.config import settings
from app.models.users import User, Role
from app.models.auth import RefreshToken
from app.api.v1.schemas.auth import TokenStatus
from app.core.security import decode_token
from app.models.images import Image, ProfileImage
from app.api.v1.schemas.users import RoleCreateV1
from app.api.v1.repositories.user_repo import user_repo_v1
from app.api.v1.repositories.auth_repo import auth_repo_v1
from app.api.v1.schemas.images import ImageInDBV1, ImageReadV1

from app.core.exceptions import (
    UserNotFoundError,
    RoleExistsError,
    ProfileImageExistsError,
    ProfileImageError,
    ServerError,
    AuthenticationError
)


class UserServiceV1:
    @staticmethod
    def get_user_by_id(user_id: UUID, db: Session) -> User:
        user = user_repo_v1.get_user_by_id(user_id, db)
        if not user:
            raise UserNotFoundError()
        return user

    @staticmethod
    def get_user_by_email(email: str, db: Session) -> User:
        user = user_repo_v1.get_user_by_email(email, db)
        if not user:
            raise UserNotFoundError()
        return user

    @staticmethod
    def get_user_by_username(username: str, db: Session) -> User:
        user = user_repo_v1.get_user_by_username(username, db)
        if not user:
            raise UserNotFoundError()
        return user

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
            raise RoleExistsError()

        role_db = Role(name=role_create.name)

        try:
            user_repo_v1.create_role(role_db, db)
            db.commit()
        except Exception as e:
            db.rollback()
            raise ServerError() from e
        finally:
            db.close()

        role_out = user_repo_v1.get_role(role_db.name, db)
        return role_out

    @staticmethod
    async def upload_image(refresh_token: RefreshToken, user: User, image_uploads: list[UploadFile], db: Session):
        token = decode_token(refresh_token, settings.REFRESH_TOKEN_SECRET_KEY)
        refresh_token_db = auth_repo_v1.get_refresh_token(token.get('jti'), db)

        if refresh_token_db.status == TokenStatus.REVOKED:
            raise AuthenticationError()

        #restricts a user from uploading 0 or more than 2 images
        if len(image_uploads) < 1 or len(image_uploads) > 2:
            raise ProfileImageError()

        user_images = user_repo_v1.get_user_images(user)

        #checks if the user already uploaded both avatar and header images
        if len(user_images) >= 2:
            raise ProfileImageExistsError()

        for img in image_uploads:
            image_id = user_repo_v1.get_image_id(img.filename, db)


            #this ensures a duplicate image is not created
            #and the profile image is created directly instead
            if image_id:
                profile_img = ProfileImage(user_id=user.id, image_id=image_id)
                try:
                    user_repo_v1.create_profile_image(profile_img, db)
                    db.commit()
                except Exception as e:
                    db.rollback()
                    raise ServerError() from e
            else:
                path = Path(settings.PROFILE_IMAGE_PATH).resolve()
                file_path = f'{str(path)}\\{img.filename}'

                await write_file(file_path, img)
                image_name = img.filename
                image_type = img.content_type
                image_size = img.size
                image = Image(
                    **ImageInDBV1(
                        image_url=image_name, image_type=image_type, image_size=image_size
                    ).model_dump()
                )
                try:
                    user_repo_v1.create_image(user, image, db)
                    db.commit()
                except Exception as e:
                    db.rollback()
                    raise ServerError() from e

        profile_images = user_repo_v1.get_user_images(user)

        image_urls = []
        for i in profile_images:
            image_urls.append(i.image.image_url)

        images = ImageReadV1(image_url=image_urls)
        return images

    @staticmethod
    def delete_user_accounts(db: Session):
        try:
            user_repo_v1.delete_user(db)
            db.commit()
        except Exception as e:
            db.rollback()
            raise ServerError() from e
        finally:
            db.close()


user_service_v1 = UserServiceV1()
