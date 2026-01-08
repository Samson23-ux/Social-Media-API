import enum
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from sqlalchemy import Column, UUID, text, Text, ForeignKey, Enum, DateTime

from app.database.base import Base

class TokenStatus(str, enum.Enum):
    VALID: str = 'valid'
    REVOKED: str = 'revoked'
    USED: str = 'used'

class RefreshToken(Base):
    __tablename__ = 'refresh_tokens'

    id = Column(UUID, default=text('uuid_generate_v4()'), primary_key=True)
    token = Column(Text, nullable=False, index=True)
    user_id = Column(UUID, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    status = Column(Enum(TokenStatus), default=TokenStatus.VALID, nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False
    )
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True))
    revoked_at = Column(DateTime(timezone=True))

    user = relationship('User', back_populates='refresh_tokens')
