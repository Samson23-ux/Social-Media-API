from uuid import UUID
from sqlalchemy.orm import Session

from app.models.users import User

class UserRepoV1:
    @staticmethod
    async def get_user_by_id(user_id: UUID, db: Session) -> User | None:
        user: User = db.query(User).filter(User.id == str(user_id)).first()
        return user

user_repo_v1 = UserRepoV1()