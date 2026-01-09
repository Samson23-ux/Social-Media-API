from uuid import UUID
from sqlalchemy.orm import Session

from app.models.users import User
from app.api.v1.repositories.user_repo import user_repo_v1
from app.core.exceptions import UserNotFoundError


class UserServiceV1:
    @staticmethod
    async def get_user_by_id(user_id: UUID, db: Session) -> User:
        user = await user_repo_v1.get_user_by_id(user_id, db)
        if not user:
            raise UserNotFoundError()
        return user

user_service_v1 = UserServiceV1()
