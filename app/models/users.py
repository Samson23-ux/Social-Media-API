import enum
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
    Date
)

from app.database.base import Base

class UserRole(str, enum.Enum):
    USER: str = 'user'
    ADMIN: str = 'admin'


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
    email = Column(VARCHAR(50), unique=True, nullable=False)
    dob = Column(Date, nullable=False)
    nationality = Column(VARCHAR(50), nullable=False)
    hash_password = Column(VARCHAR(50), nullable=False)
    role_id = Column(UUID, ForeignKey('roles.id', ondelete='RESTRICT'), nullable=False)
    bio = Column(Text)
    is_delete = Column(Boolean, default=False, nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False
    )
    deleted_at = Column(DateTime(timezone=True))
    delete_at = Column(DateTime(timezone=True))

    @property
    def age(self):
        #returns the user age
        today: date = date.today()
        return (
            - today.year
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

    comments = relationship(
        'Comment',
        secondary='comments',
        back_populates='user',
        passive_deletes=True,
        cascade='all, delete-orphan',
        single_parent=True,
    )

    likes = relationship(
        'Like',
        secondary='likes',
        back_populates='user',
        passive_deletes=True,
        cascade='all, delete-orphan',
        single_parent=True,
    )

    role = relationship('Role', back_populates='users')

    refresh_tokens = relationship(
        'RefreshToken', back_populates='user', passive_deletes=True
    )

    profile_images = relationship(
        'ProfileImage',
        back_populates='user',
        cascade='all, delete-orphan',
        single_parent=True,
        passive_deletes=True,
    )

    post_images = relationship(
        'PostImage',
        secondary='user',
        passive_deletes=True,
        cascade='all, delete-orphan',
        single_parent=True,
    )


class ProfileImage(Base):
    # holds both avatar and header image urls
    # a user should only appear twice with logic enforced in app layer
    __tablename__ = 'profile_images'

    id = Column(UUID, default=text('uuid_generate_v4()'), primary_key=True)
    user_id = Column(UUID, ForeignKey('users.id', ondelete='CASCADE'))
    image_url = Column(Text, nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False
    )

    user = relationship('User', back_populates='profile_images')


class Role(Base):
    __tablename__ = 'roles'

    id = Column(UUID, default=text('uuid_generate_v4()'), primary_key=True)
    name = Column(Enum(UserRole), nullable=False, unique=True)

    users = relationship('User', back_populates='role', passive_deletes=True)
