from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from sqlalchemy import Column, VARCHAR, UUID, DateTime, text, Integer, ForeignKey

from app.database.base import Base


class Image(Base):
    __tablename__ = 'images'

    id = Column(UUID, default=text('uuid_generate_v4()'), primary_key=True)
    image_url = Column(VARCHAR(20), nullable=False)
    image_type = Column(VARCHAR(20), nullable=False)
    image_size = Column(Integer, nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False
    )

    users = relationship(
        'User', secondary='profile_images', back_populates='images', viewonly=True
    )

    profile_images = relationship(
        'ProfileImage',
        back_populates='image',
        viewonly=True,
    )

    posts = relationship(
        'Post', secondary='post_images', back_populates='images', viewonly=True
    )

    post_images = relationship('PostImage', back_populates='image', viewonly=True)


class ProfileImage(Base):
    # holds both avatar and header image urls
    # a user should only appear twice with logic enforced in app layer
    __tablename__ = 'profile_images'

    id = Column(UUID, default=text('uuid_generate_v4()'), primary_key=True)
    user_id = Column(UUID, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    image_id = Column(UUID, ForeignKey('images.id', ondelete='CASCADE'), nullable=False)

    user = relationship('User', back_populates='profile_images', viewonly=True)
    image = relationship('Image', back_populates='profile_images', viewonly=True)


class PostImage(Base):
    __tablename__ = 'post_images'

    id = Column(UUID, default=text('uuid_generate_v4()'), primary_key=True)
    post_id = Column(UUID, ForeignKey('posts.id', ondelete='CASCADE'), nullable=False)
    image_id = Column(UUID, ForeignKey('images.id', ondelete='CASCADE'), nullable=False)

    post = relationship('Post', back_populates='post_images', viewonly=True)
    image = relationship('Image', back_populates='post_images', viewonly=True)
