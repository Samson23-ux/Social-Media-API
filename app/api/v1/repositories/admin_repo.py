from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_

from app.models.users import User


class AdminRepoV1:
    @staticmethod
    def count_users(role_id: UUID, db: Session) -> int:
        stmt = select(func.count()).where(
            and_(
                User.is_delete.is_(False),
                User.is_suspended.is_(False),
                User.role_id != role_id,
            )
        )

        users: int = db.execute(stmt).scalar()
        return users

    @staticmethod
    def get_suspended_users(role_id: UUID, db: Session) -> list[User]:
        stmt = select(User).where(
            and_(
                User.is_delete.is_(False),
                User.is_suspended.is_(True),
                User.role_id != role_id,
            )
        )

        users: list[User] = db.execute(stmt).scalars().all()
        return users

    @staticmethod
    def get_suspended_user(role_id: UUID, username: str, db: Session) -> User | None:
        stmt = select(User).where(
            and_(
                User.username == username,
                User.is_delete.is_(False),
                User.is_suspended.is_(True),
                User.role_id != role_id,
            )
        )
        user: User | None = db.execute(stmt).scalar()
        return user


admin_repo_v1 = AdminRepoV1()
