from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from sqlalchemy import Column, UUID, Text, ForeignKey, Enum, DateTime

from app.database.base import Base
from app.api.v1.schemas.auth import TokenStatus

class RefreshToken(Base):
    __tablename__ = 'refresh_tokens'

    id = Column(UUID, primary_key=True)
    token = Column(Text, nullable=False, index=True)
    user_id = Column(
        UUID, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True
    )
    status = Column(Enum(TokenStatus), default=TokenStatus.VALID, nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False
    )
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True))
    revoked_at = Column(DateTime(timezone=True))

    user = relationship('User', back_populates='refresh_tokens')
