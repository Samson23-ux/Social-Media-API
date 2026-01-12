from uuid import UUID
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from sqlalchemy import select, delete, and_

from app.models.users import User, Role
from app.models.images import Image, ProfileImage


class UserRepoV1:
    @staticmethod
    def get_user_by_id(user_id: UUID, db: Session) -> User | None:
        stmt = select(User).where(
            and_(User.id == str(user_id), User.is_delete.is_(False))
        )
        user: User = db.execute(stmt).scalar()
        return user

    @staticmethod
    def get_user_by_username(username: str, db: Session) -> User | None:
        stmt = select(User).where(
            and_(User.username == username, User.is_delete.is_(False))
        )
        user: User = db.execute(stmt).scalar()
        return user

    @staticmethod
    def get_user_by_email(email: str, db: Session) -> User | None:
        stmt = select(User).where(and_(User.email == email, User.is_delete.is_(False)))
        user: User = db.execute(stmt).scalar()
        return user

    @staticmethod
    def get_deleted_users(email: str, db: Session) -> User | None:
        stmt = select(User).where(and_(User.email == email, User.is_delete.is_(True)))
        user: User = db.execute(stmt).scalar()
        return user

    @staticmethod
    def get_role(role_name: str, db: Session) -> Role | None:
        stmt = select(Role).where(Role.name == role_name)
        role: Role = db.execute(stmt).scalar()
        return role

    @staticmethod
    def get_user_images(user: User) -> list[ProfileImage]:
        return user.profile_images

    @staticmethod
    def get_image_id(image_url: str, db: Session) -> UUID:
        stmt = select(Image.id).where(Image.image_url == image_url)
        image_id = db.execute(stmt).scalar()
        return image_id

    @staticmethod
    def add_user(user: User, db: Session):
        db.add(user)
        db.flush()
        db.refresh(user)

    @staticmethod
    def create_image(user: User, image: Image, db: Session):
        user.images.append(image)
        db.flush()
        db.refresh(user)

    @staticmethod
    def create_profile_image(image: ProfileImage, db: Session):
        db.add(image)
        db.flush()
        db.refresh(image)

    @staticmethod
    def create_role(role: Role, db: Session):
        db.add(role)
        db.flush()
        db.refresh(role)

    @staticmethod
    def delete_user(db: Session):
        stmt = (
            delete(User)
            .where(datetime.now(timezone.utc) >= User.delete_at)
            .execution_options(synchronize_session='fetch')
        )
        db.execute(stmt)


user_repo_v1 = UserRepoV1()
