from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_

from app.models.users import User


class AdminRepoV1:
    @staticmethod
    def count_users(db: Session) -> int:
        stmt = select(func.count()).where(
            and_(User.is_delete.is_(False), User.is_suspended.is_(False))
        )

        users: int = db.execute(stmt).scalar()
        return users

    @staticmethod
    def get_suspended_users(db: Session) -> list[User]:
        stmt = select(User).where(User.is_suspended.is_(True))

        users: list[User] = db.execute(stmt).scalars()
        return users


admin_repo_v1 = AdminRepoV1()
