import enum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy import (
    Column,
    VARCHAR,
    text,
    Text,
    ForeignKey,
    Enum,
    DateTime,
    UUID,
    Computed,
    Index,
)

from app.database.base import Base


class VisibilityEnum(str, enum.Enum):
    PUBLIC: str = 'public'
    FOLLOWERS: str = 'followers'
    PRIVATE: str = 'private'


class Post(Base):
    __tablename__ = 'posts'

    id = Column(UUID, default=text('uuid_generate_v4()'), primary_key=True)
    title = Column(VARCHAR(50), nullable=False)
    content = Column(Text, nullable=False)
    content_search = Column(
        TSVECTOR, Computed("to_tsvector('english', \'content\')", persisted=True)
    )
    user_id = Column(UUID, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    visibility = Column(
        Enum(VisibilityEnum), default=VisibilityEnum.PUBLIC, nullable=False
    )
    created_at = Column(
        DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False
    )

    user = relationship('User', back_populates='posts', viewonly=True)

    comments = relationship(
        'Comment',
        back_populates='post',
        passive_deletes=True,
        cascade='all, delete-orphan',
        single_parent=True,
    )

    likes = relationship(
        'Like',
        back_populates='post',
        passive_deletes=True,
        cascade='all, delete-orphan',
        single_parent=True,
    )

    images = relationship('Image', secondary='post_images', back_populates='posts')

    post_images = relationship('PostImage', back_populates='post', viewonly=True)

    __table_args__ = (
        Index('idx_content_search', content_search, postgresql_using='gin'),
    )


class Like(Base):
    __tablename__ = 'likes'

    post_id = Column(UUID, ForeignKey('posts.id', ondelete='CASCADE'), primary_key=True)
    user_id = Column(UUID, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    liked_at = Column(
        DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False
    )

    post = relationship('Post', back_populates='likes')
    user = relationship('User', back_populates='likes')


class Comment(Base):
    __tablename__ = 'comments'

    id = Column(UUID, default=text('uuid_generate_v4()'), primary_key=True)
    post_id = Column(UUID, ForeignKey('posts.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(UUID, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False
    )

    user = relationship('User', back_populates='comments')
    post = relationship('Post', back_populates='comments')
