from sqlalchemy.orm import relationship
from datetime import datetime, timezone, date
from sqlalchemy import (
    Column,
    VARCHAR,
    text,
    ForeignKey,
    Text,
    DateTime,
    Boolean,
    Table,
    UUID,
    Enum,
    Date,
    Index,
)

from app.database.base import Base
from app.api.v1.schemas.users import UserRole


follows = Table(
    'follows',
    Base.metadata,
    Column(
        'following_id',
        UUID,
        ForeignKey('users.id', ondelete='CASCADE'),
        primary_key=True,
    ),
    Column(
        'follower_id',
        UUID,
        ForeignKey('users.id', ondelete='CASCADE'),
        primary_key=True,
    ),
)


class User(Base):
    __tablename__ = 'users'

    id = Column(UUID, default=text('uuid_generate_v4()'), primary_key=True)
    display_name = Column(VARCHAR(50), nullable=False)
    username = Column(VARCHAR(50), nullable=False, unique=True)
    email = Column(VARCHAR(50), unique=True, nullable=False, index=True)
    dob = Column(Date, nullable=False)
    nationality = Column(VARCHAR(50), nullable=False, index=True)
    hash_password = Column(Text, nullable=False)
    role_id = Column(
        UUID, ForeignKey('roles.id', ondelete='RESTRICT'), nullable=False, index=True
    )
    bio = Column(Text)
    is_suspended = Column(Boolean, default=False, nullable=False)
    is_delete = Column(Boolean, default=False, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    suspended_at = Column(DateTime(timezone=True))
    deleted_at = Column(DateTime(timezone=True))
    delete_at = Column(DateTime(timezone=True))

    # only visible to the owner's account
    @property
    def age(self):
        # returns the user age
        today: date = date.today()
        return (
            today.year
            - self.dob.year
            - ((today.month, today.day) < (self.dob.month, self.dob.day))
        )

    following = relationship(
        'User',
        secondary='follows',
        primaryjoin=id == follows.c.follower_id,
        secondaryjoin=id == follows.c.following_id,
        passive_deletes=True,
        backref='followers',
    )

    posts = relationship(
        'Post',
        back_populates='user',
        passive_deletes=True,
        cascade='all, delete-orphan',
        single_parent=True,
    )

    comments = relationship('Comment', back_populates='user', viewonly=True)

    comment_likes = relationship(
        'CommentLike',
        passive_deletes=True,
        cascade='all, delete-orphan',
        single_parent=True,
        back_populates='user',
    )

    likes = relationship('Like', back_populates='user', viewonly=True)

    role = relationship('Role', back_populates='users')

    refresh_tokens = relationship(
        'RefreshToken', back_populates='user', passive_deletes=True
    )

    # This allows the profile_images table to be updated with
    # the user_id and image_id upon insertion of image into
    # user.images collection
    images = relationship('Image', secondary='profile_images', back_populates='users')

    profile_images = relationship('ProfileImage', back_populates='user', viewonly=True)

    __table_args__ = (
        Index(
            'idx_display_name',
            display_name,
            postgresql_using='gin',
            postgresql_ops={'display_name': 'gin_trgm_ops'},
        ),
        Index(
            'idx_username',
            username,
            postgresql_using='gin',
            postgresql_ops={'username': 'gin_trgm_ops'},
        ),
    )


class Role(Base):
    __tablename__ = 'roles'

    id = Column(UUID, default=text('uuid_generate_v4()'), primary_key=True)
    name = Column(Enum(UserRole), nullable=False, unique=True)

    users = relationship('User', back_populates='role', passive_deletes=True)
