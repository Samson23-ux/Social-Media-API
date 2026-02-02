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
    PrimaryKeyConstraint,
    UniqueConstraint,
)

from app.database.base import Base
from app.api.v1.schemas.users import UserRole


follows = Table(
    'follows',
    Base.metadata,
    Column(
        'following_id',
        UUID,
        ForeignKey('users.id', name='following_id_fk', ondelete='CASCADE'),
    ),
    Column(
        'follower_id',
        UUID,
        ForeignKey('users.id', name='follower_id_fk', ondelete='CASCADE'),
    ),
    PrimaryKeyConstraint('following_id', 'follower_id', name='follows_pk'),
)


class User(Base):
    __tablename__ = 'users'

    id = Column(UUID, default=text('uuid_generate_v4()'))
    display_name = Column(VARCHAR(50), nullable=False)
    username = Column(VARCHAR(50), nullable=False)
    email = Column(VARCHAR(50), nullable=False)
    dob = Column(Date, nullable=False)
    nationality = Column(VARCHAR(50), nullable=False)
    hash_password = Column(Text, nullable=False)
    role_id = Column(
        UUID,
        ForeignKey('roles.id', name='role_id_fk', ondelete='RESTRICT'),
        nullable=False,
    )
    bio = Column(Text)
    is_suspended = Column(Boolean, default=False, nullable=False)
    is_delete = Column(Boolean, default=False, nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False
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
        PrimaryKeyConstraint('id', name='users_pk'),
        UniqueConstraint('username', name='username_unique_key'),
        UniqueConstraint('email', name='email_unique_key'),
        Index(
            'idx_user_display_name',
            display_name,
            postgresql_using='gin',
            postgresql_ops={'display_name': 'gin_trgm_ops'},
        ),
        Index(
            'idx_user_username',
            username,
            postgresql_using='gin',
            postgresql_ops={'username': 'gin_trgm_ops'},
        ),
        Index('idx_user_email', email),
        Index('idx_user_nationality', nationality),
        Index('idx_user_role_id', role_id),
        Index('idx_user_created_at', created_at),
    )


class Role(Base):
    __tablename__ = 'roles'

    id = Column(UUID, default=text('uuid_generate_v4()'))
    name = Column(Enum(UserRole), nullable=False)

    users = relationship('User', back_populates='role', passive_deletes=True)

    __table_args__ = (
        PrimaryKeyConstraint('id', name='roles_pk'),
        UniqueConstraint('name', name='name_unique_key'),
    )
