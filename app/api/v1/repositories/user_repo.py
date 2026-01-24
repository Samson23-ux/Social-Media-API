from uuid import UUID
from typing import Any
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from sqlalchemy import select, delete, and_, func, desc, or_

from app.models.users import User, Role
from app.models.posts import Post, Like, Comment
from app.models.images import Image, ProfileImage
from app.api.v1.schemas.posts import VisibilityEnum


class UserRepoV1:
    @staticmethod
    def get_users(
        db: Session,
        nationality: str | None = None,
        year: int | None = None,
        sort: str | None = None,
        order: str | None = None,
        offset: int = 0,
        limit: int = 10,
    ) -> list[User]:
        '''get users with filtering, sorting and pagination'''

        # the possible fields to sort by
        # this prevents sorting by a field that does not exist
        sortable_fields: dict[str, Any] = {
            'username': User.username,
            'created_at': User.created_at,
            'nationality': User.nationality,
            'display_name': User.display_name,
        }
        stmt = select(User)

        stmt = stmt.where(User.is_delete.is_(False))

        if nationality:
            stmt = stmt.where(func.lower(User.nationality) == func.lower(nationality))

        if year:
            stmt = stmt.where(User.dob.year == year)

        if sort:
            if order == 'desc':
                stmt = stmt.order_by(desc(sortable_fields.get(sort, User.created_at)))
            else:
                stmt = stmt.order_by(sortable_fields.get(sort, User.created_at))

        stmt = stmt.offset(offset).limit(limit)
        users = db.execute(stmt).scalars().all()

        return users

    @staticmethod
    def search_users(
        db: Session,
        q: str,
        nationality: str | None = None,
        year: int | None = None,
        sort: str | None = None,
        order: str | None = None,
        offset: int = 0,
        limit: int = 10,
    ) -> list[User]:
        '''get users with filtering, sorting and pagination'''

        # the possible fields to sort by
        # this prevents sorting by a field that does not exist
        sortable_fields: dict[str, Any] = {
            'username': User.username,
            'created_at': User.created_at,
            'nationality': User.nationality,
            'display_name': User.display_name,
        }
        stmt = select(User)

        stmt = stmt.where(
            and_(
                or_(User.display_name.ilike(q), User.username.ilike(q)),
                User.is_created.is_(False),
            )
        )

        if nationality:
            stmt = stmt.where(func.lower(User.nationality) == func.lower(nationality))

        if year:
            stmt = stmt.where(User.dob.year == year)

        if sort:
            if order == 'desc':
                stmt = stmt.order_by(desc(sortable_fields.get(sort, User.created_at)))
            else:
                stmt = stmt.order_by(sortable_fields.get(sort, User.created_at))

        stmt = stmt.offset(offset).limit(limit)
        users = db.execute(stmt).scalars().all()

        return users

    @staticmethod
    def get_followers(user: User) -> list[User] | None:
        return user.followers

    @staticmethod
    def get_followings(user: User) -> list[User] | None:
        return user.following

    @staticmethod
    def get_user_by_id(user_id: UUID, db: Session) -> User | None:
        stmt = select(User).where(and_(User.id == user_id, User.is_delete.is_(False)))
        user: User | None = db.execute(stmt).scalar()
        return user

    @staticmethod
    def get_user_by_username(username: str, db: Session) -> User | None:
        stmt = select(User).where(
            and_(User.username == username, User.is_delete.is_(False))
        )
        user: User | None = db.execute(stmt).scalar()
        return user

    @staticmethod
    def get_user_by_email(email: str, db: Session) -> User | None:
        stmt = select(User).where(and_(User.email == email, User.is_delete.is_(False)))
        user: User | None = db.execute(stmt).scalar()
        return user

    @staticmethod
    def get_deleted_user(email: str, db: Session) -> User | None:
        stmt = select(User).where(and_(User.email == email, User.is_delete.is_(True)))
        user: User | None = db.execute(stmt).scalar()
        return user

    @staticmethod
    def get_role(role_name: str, db: Session) -> Role | None:
        stmt = select(Role).where(Role.name == role_name)
        role: Role | None = db.execute(stmt).scalar()
        return role

    @staticmethod
    def get_current_user_posts(
        user_id: UUID,
        db: Session,
        created_at: int | None = None,
        sort: str | None = None,
        order: str | None = None,
        offset: int = 0,
        limit: int = 10,
    ) -> list | None:
        '''select current user's posts and handle sorting by likes and comments'''

        sortable_fields: list[str] = ['created_at', 'likes', 'comments']
        stmt = select(
            Post.id,
            Post.title,
            Post.content,
            Post.visibility,
            Post.created_at,
            User.display_name,
            User.username,
        ).join(User, Post.user_id == user_id)

        # filter by date created if set
        if created_at:
            stmt = stmt.where(Post.created_at.year == created_at)

        '''the control flow below sort by one of the sortable fields
        for the likes and comments, a column is generated as likes/comments
        that represents the total number of likes/comments for the post
        done by joining the posts table with likes/comments and grouping
        by post then using the window function count to get the total
        likes/comments'''
        stmt = (
            stmt.select(
                func.count(Comment.user_id).label('comments'),
                func.count(Like.user_id).label('likes'),
            )
            .join(Post, Post.id == Comment.post_id)
            .join(Post, Post.id == Like.post_id)
            .group_by(Comment.post_id)
        )

        if sort not in sortable_fields or sort == 'created_at':
            if order == 'desc':
                stmt = stmt.order_by(desc(Post.created_at))
            else:
                stmt = stmt.order_by(Post.created_at)
        elif sort == 'likes':
            if order == 'desc':
                stmt = stmt.order_by(desc('likes'))
            else:
                stmt = stmt.order_by('likes')
        elif sort == 'comments':
            if order == 'desc':
                stmt = stmt.order_by(desc('comments'))
            else:
                stmt = stmt.order_by('comments')

        stmt = stmt.offset(offset).limit(limit)
        user_posts: list | None = db.execute(stmt).all()
        return user_posts

    @staticmethod
    def get_user_posts(
        current_user: User,
        user: User,
        user_id: UUID,
        db: Session,
        created_at: int | None = None,
        sort: str | None = None,
        order: str | None = None,
        offset: int = 0,
        limit: int = 10,
    ):
        '''since the request is to get another user's posts
        an additional check is required to only get posts
        whose visibility is set to followers if the current
        user is follwer in addition to public posts'''

        sortable_fields: list[str] = ['created_at', 'likes', 'comments']
        if current_user in user.followers:
            stmt = (
                select(
                    Post.id,
                    Post.title,
                    Post.content,
                    Post.visibility,
                    Post.created_at,
                    User.display_name,
                    User.username,
                )
                .join(User, Post.user_id == user_id)
                .where(
                    or_(
                        Post.visibility == VisibilityEnum.PUBLIC,
                        Post.visibility == VisibilityEnum.FOLLOWERS,
                    )
                )
            )
        else:
            stmt = (
                select(
                    Post.id,
                    Post.title,
                    Post.content,
                    Post.visibility,
                    Post.created_at,
                    User.display_name,
                    User.username,
                )
                .join(User, Post.user_id == user_id)
                .where(
                    or_(
                        Post.visibility == VisibilityEnum.PUBLIC,
                    )
                )
            )

        # same filter and sort process as get current user posts
        if created_at:
            stmt = stmt.where(Post.created_at.year == created_at)

        stmt = (
            stmt.select(
                func.count(Comment.user_id).label('comments'),
                func.count(Like.user_id).label('likes'),
            )
            .join(Post, Post.id == Comment.post_id)
            .join(Post, Post.id == Like.post_id)
            .group_by(Comment.post_id)
        )

        if sort not in sortable_fields or sort == 'created_at':
            if order == 'desc':
                stmt = stmt.order_by(desc(Post.created_at))
            else:
                stmt = stmt.order_by(Post.created_at)
        elif sort == 'likes':
            if order == 'desc':
                stmt = stmt.order_by(desc('likes'))
            else:
                stmt = stmt.order_by('likes')
        elif sort == 'comments':
            if order == 'desc':
                stmt = stmt.order_by(desc('comments'))
            else:
                stmt = stmt.order_by('comments')

        stmt = stmt.offset(offset).limit(limit)
        user_posts: list | None = db.execute(stmt).all()
        return user_posts

    @staticmethod
    def get_user_comments(user: User) -> list[Comment] | None:
        return user.comments

    @staticmethod
    def get_liked_posts(
        user_id: UUID,
        db: Session,
        offset: int = 0,
        limit: int = 10,
    ) -> list:
        stmt = (
            select(
                User.display_name,
                User.username,
                Post.id,
                Post.title,
                Post.content,
                Post.visibility,
                Post.created_at,
            )
            .join(Like, user_id == Like.user_id)
            .join(Post, Post.id == Like.post_id)
            .offset(offset)
            .limit(limit)
        )

        liked_posts = db.execute(stmt).all()
        return liked_posts

    @staticmethod
    def get_user_images(user: User) -> list[ProfileImage]:
        return user.profile_images

    @staticmethod
    def get_user_avatar(image_url: str, user_id: UUID, db: Session) -> str:
        stmt = (
            select(Image.image_url)
            .join(User, user_id == ProfileImage.user_id)
            .join(Image, Image.id == ProfileImage.image_id)
            .where(Image.image_url == image_url)
        )
        return db.execute(stmt).scalar()

    @staticmethod
    def get_image_id(image_url: str, db: Session) -> UUID:
        stmt = select(Image.id).where(Image.image_url == image_url)
        image_id: UUID = db.execute(stmt).scalar()
        return image_id

    @staticmethod
    def add_user(user: User, db: Session):
        db.add(user)
        db.flush()
        db.refresh(user)

    @staticmethod
    def follow_user(current_user: User, user: User, db: Session):
        current_user.following.append(user)
        db.flush()
        db.refresh(user)

    @staticmethod
    def create_image(user: User, image: Image, db: Session):
        user.images.append(image)
        db.flush()
        db.refresh(user)

    @staticmethod
    def create_profile_image(image: ProfileImage, db: Session):
        db.add(image)
        db.flush()
        db.refresh(image)

    @staticmethod
    def create_role(role: Role, db: Session):
        db.add(role)
        db.flush()
        db.refresh(role)

    @staticmethod
    def unfollow_user(current_user: User, user: User, db: Session):
        current_user.following.remove(user)
        db.flush()
        db.refresh(user)

    @staticmethod
    def delete_user(db: Session):
        stmt = (
            delete(User)
            .where(datetime.now(timezone.utc) >= User.delete_at)
            .execution_options(synchronize_session='fetch')
        )
        db.execute(stmt)


user_repo_v1 = UserRepoV1()
