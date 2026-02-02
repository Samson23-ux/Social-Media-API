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
    PrimaryKeyConstraint
)

from app.database.base import Base
from app.api.v1.schemas.posts import VisibilityEnum


class Post(Base):
    __tablename__ = 'posts'

    id = Column(UUID, default=text('uuid_generate_v4()'))
    title = Column(VARCHAR(50), nullable=False)
    content = Column(Text, nullable=False)
    content_search = Column(
        TSVECTOR, Computed("to_tsvector('english', \'content\')", persisted=True)
    )
    user_id = Column(
        UUID, ForeignKey('users.id', name='user_id_fk', ondelete='CASCADE'), nullable=False
    )
    visibility = Column(
        Enum(VisibilityEnum), default=VisibilityEnum.PUBLIC, nullable=False
    )
    created_at = Column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
        nullable=False
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
        PrimaryKeyConstraint('id', name='posts_pk'),
        Index('idx_post_user_id', user_id),
        Index('idx_post_created_at', created_at),
        Index('idx_post_content_search', content_search, postgresql_using='gin'),
        Index(
            'idx_post_title',
            title,
            postgresql_using='gin',
            postgresql_ops={'title': 'gin_trgm_ops'},
        ),
    )


class Like(Base):
    __tablename__ = 'likes'

    post_id = Column(
        UUID, ForeignKey('posts.id', ondelete='CASCADE')
    )
    user_id = Column(
        UUID, ForeignKey('users.id', ondelete='CASCADE')
    )
    liked_at = Column(
        DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False
    )

    post = relationship('Post', back_populates='likes')
    user = relationship('User', back_populates='likes')

    __table_args__ = (
        PrimaryKeyConstraint('post_id', 'user_id', name='likes_pk'),
        Index('idx_like_post_id', post_id),
        Index('idx_like_user_id', user_id)
    )


class Comment(Base):
    __tablename__ = 'comments'

    id = Column(UUID, default=text('uuid_generate_v4()'))
    post_id = Column(
        UUID, ForeignKey('posts.id', name='post_id_fk', ondelete='CASCADE'), nullable=False
    )
    user_id = Column(
        UUID, ForeignKey('users.id', name='user_id_fk', ondelete='CASCADE'), nullable=False
    )
    content = Column(Text, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
        nullable=False,
    )

    user = relationship('User', back_populates='comments')
    post = relationship('Post', back_populates='comments')
    comment_likes = relationship(
        'CommentLike',
        passive_deletes=True,
        cascade='all, delete-orphan',
        single_parent=True,
        back_populates='comment',
    )


    __table_args__ = (
        PrimaryKeyConstraint('id', name='comments_pk'),
        Index('idx_comment_post_id', post_id),
        Index('idx_comment_user_id', user_id),
        Index('idx_comment_created_at', created_at)
    )


class CommentLike(Base):
    __tablename__ = 'comment_likes'

    user_id = Column(
        UUID,
        ForeignKey('users.id', name='user_id_fk', ondelete='CASCADE'),
    )
    comment_id = Column(
        UUID,
        ForeignKey('comments.id', name='comment_id_fk', ondelete='CASCADE'),
    )
    liked_at = Column(
        DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False
    )

    user = relationship('User', back_populates='comment_likes', viewonly=True)
    comment = relationship('Comment', back_populates='comment_likes', viewonly=True)


    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'comment_id', name='comment_likes_pk'),
        Index('idx_comment_like_comment_id', comment_id)
    )
