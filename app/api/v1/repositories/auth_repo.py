from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select, delete, or_

from app.models.auth import RefreshToken
from app.api.v1.schemas.auth import TokenStatus


class AuthRepoV1:
    @staticmethod
    def get_refresh_token(token_id: UUID, db: Session) -> RefreshToken:
        stmt = select(RefreshToken).where(RefreshToken.id == str(token_id))
        token: RefreshToken | None = db.execute(stmt).scalar()
        return token

    @staticmethod
    def store_refresh_token(token: RefreshToken, db: Session):
        '''create and update refresh token'''
        db.add(token)
        db.flush()
        db.refresh(token)

    @staticmethod
    def delete_tokens(db: Session):
        stmt = (
            delete(RefreshToken)
            .where(
                or_(
                    datetime.now(timezone.utc) >= RefreshToken.expires_at,
                    RefreshToken.status == TokenStatus.REVOKED,
                    RefreshToken.status == TokenStatus.USED,
                )
            )
            .execution_options(synchronize_session=False)
        )
        db.execute(stmt)


auth_repo_v1 = AuthRepoV1()
