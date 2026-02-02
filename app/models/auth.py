from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column,
    UUID,
    Text,
    Enum,
    DateTime,
    PrimaryKeyConstraint,
    Index,
    ForeignKey,
)

from app.database.base import Base
from app.api.v1.schemas.auth import TokenStatus


class RefreshToken(Base):
    __tablename__ = 'refresh_tokens'

    id = Column(UUID)
    token = Column(Text, nullable=False)
    user_id = Column(
        UUID,
        ForeignKey('users.id', name='user_id_fk', ondelete='CASCADE'),
        nullable=False,
    )
    status = Column(Enum(TokenStatus), default=TokenStatus.VALID, nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False
    )
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True))
    revoked_at = Column(DateTime(timezone=True))

    user = relationship('User', back_populates='refresh_tokens')

    __table_args__ = (
        PrimaryKeyConstraint('id', name='refresh_tokens_pk'),
        Index('idx_auth_token', token),
        Index('idx_auth_user_id', user_id),
    )
