import os
import sentry_sdk
from uuid import UUID
from pathlib import Path
from fastapi import UploadFile
from sqlalchemy.orm import Session
from sentry_sdk import logger as sentry_logger


from app.core.config import settings
from app.models.users import User, Role
from app.models.posts import Post, Comment
from app.utils import write_file, validate_image
from app.api.v1.schemas.images import ImageReadV1
from app.models.images import Image, ProfileImage
from app.core.security import validate_refresh_token
from app.api.v1.repositories.user_repo import user_repo_v1
from app.api.v1.repositories.post_repo import post_repo_v1
from app.api.v1.schemas.posts import PostReadV1, CommentReadV1
from app.api.v1.schemas.users import (
    UserReadV1,
    UserUpdateV1,
    RoleCreateV1,
    UserProfileV1,
    CurrentUserProfileV1,
)

from app.core.exceptions import (
    ServerError,
    RoleExistsError,
    UserExistsError,
    ImageUploadError,
    UserNotFoundError,
    InvalidImageError,
    UsersNotFoundError,
    PostsNotFoundError,
    AvatarNotFoundError,
    CommentsNotFoundError,
    FollowersNotFoundError,
    FollowingNotFoundError,
    ProfileImageExistsError,
)


class UserServiceV1:
    @staticmethod
    def get_users(
        user: User,
        db: Session,
        refresh_token: str,
        nationality: str | None = None,
        year: int | None = None,
        sort: str | None = None,
        order: str | None = None,
        offset: int = 0,
        limit: int = 10,
    ) -> list[UserReadV1]:
        _ = validate_refresh_token(refresh_token, db)

        try:
            users_db: list[User] = user_repo_v1.get_users(
                user.id, db, nationality, year, sort, order, offset, limit
            )
            if not users_db:
                sentry_logger.error('Users not found in database')
                raise UsersNotFoundError()

            users: list[UserReadV1] = []
            for user in users_db:
                user_read = UserReadV1.model_validate(user)
                users.append(user_read)

            sentry_logger.info('Users retrieved from database successfully')
            return users
        except Exception as e:
            '''raises the exceptions instead of 500 internal server error'''
            if isinstance(e, UsersNotFoundError):
                raise UsersNotFoundError()

            sentry_sdk.capture_exception(e)
            sentry_logger.error('Error occured retrieving users from database')
            raise ServerError() from e

    @staticmethod
    def search_users(
        db: Session,
        refresh_token: str,
        q: str,
        nationality: str | None = None,
        year: int | None = None,
        sort: str | None = None,
        order: str | None = None,
        offset: int = 0,
        limit: int = 10,
    ) -> list[UserReadV1]:
        _ = validate_refresh_token(refresh_token, db)

        try:
            users_db: list[User] = user_repo_v1.search_users(
                db, q, nationality, year, sort, order, offset, limit
            )
            if not users_db:
                sentry_logger.error('Searched users not found in database')
                raise UsersNotFoundError()

            users: list[UserReadV1] = []
            for user in users_db:
                user_read = UserReadV1.model_validate(user)
                users.append(user_read)

            sentry_logger.info('Searched users retrieved from database successfully')
            return users
        except Exception as e:
            '''raises the exceptions instead of 500 internal server error'''
            if isinstance(e, UserNotFoundError):
                raise UsersNotFoundError()

            sentry_sdk.capture_exception(e)
            sentry_logger.error('Error occured retrieving searched users from database')
            raise ServerError() from e

    @staticmethod
    def get_user_by_id(user_id: UUID, db: Session) -> User:
        try:
            user = user_repo_v1.get_user_by_id(user_id, db)
            if not user:
                sentry_logger.error('User with email: {id} not found', id=user_id)
                raise UserNotFoundError()
            sentry_logger.info('User {id} retrieved successfully', id=user_id)
            return user
        except Exception as e:
            '''raises the exception instead of 500 internal server error'''
            if isinstance(e, UserNotFoundError):
                raise UserNotFoundError()

            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                'Error occured while retrieving user {id} from database', id=user_id
            )
            raise ServerError() from e

    @staticmethod
    def get_user_by_email(email: str, db: Session) -> User:
        user = user_repo_v1.get_user_by_email(email, db)
        if not user:
            sentry_logger.error('User with email {email} not found', email=email)
            raise UserNotFoundError()
        return user

    @staticmethod
    def get_user_by_username(
        username: str, db: Session, refresh_token: str = None
    ) -> User:
        if refresh_token:
            _ = validate_refresh_token(refresh_token, db)

        user = user_repo_v1.get_user_by_username(username, db)
        if not user:
            sentry_logger.error(
                'User with username {username} not found', username=username
            )
            raise UserNotFoundError()
        return user

    @staticmethod
    def get_user_profile(
        username: str, refresh_token: str, db: Session
    ) -> UserProfileV1:
        '''get other user profile with username
        the age of the owner's profile is not visible to public'''
        _ = validate_refresh_token(refresh_token, db)

        user = user_repo_v1.get_user_by_username(username, db)
        if not user:
            sentry_logger.error(
                'User with username {username} not found', username=username
            )
            raise UserNotFoundError()

        # get user followers and following
        followers, following = user.followers, user.following

        user_read = UserReadV1.model_validate(user)
        user_profile = UserProfileV1(
            **user_read.model_dump(), followers=len(followers), following=len(following)
        )

        return user_profile

    @staticmethod
    def get_current_user_profile(
        user: User, refresh_token: str, db: Session
    ) -> CurrentUserProfileV1:
        '''get current user profile with username and age'''
        _ = validate_refresh_token(refresh_token, db)

        # get user followers and following
        followers, following = user.followers, user.following

        user_read = UserReadV1.model_validate(user)
        user_profile = CurrentUserProfileV1(
            **user_read.model_dump(),
            followers=len(followers),
            following=len(following),
            age=user.age,
        )

        return user_profile

    @staticmethod
    def get_role(role_name: str, db: Session) -> Role:
        role = user_repo_v1.get_role(role_name, db)
        return role

    @staticmethod
    def get_followers(
        current_user: User, username: str, refresh_token: str, db: Session
    ):
        _ = validate_refresh_token(refresh_token, db)

        user_id = current_user.id

        try:
            '''only query db if current user tries to get otheruser's followers'''
            if current_user.username == username:
                '''get the current user's followers'''
                followers: list[User] | None = user_repo_v1.get_followers(current_user)
            else:
                '''get other user's followers'''
                user: User | None = user_repo_v1.get_user_by_username(username, db)

                if not user:
                    sentry_logger.error(
                        'User with username: {username} not found', username=username
                    )
                    raise UserNotFoundError()
                user_id = user.id

                followers: list[User] | None = user_repo_v1.get_followers(user)

            if not followers:
                sentry_logger.error('User {id} followers not found', id=user_id)
                raise FollowersNotFoundError()

            sentry_logger.info(
                'User {id} followers retrieved from database', id=user_id
            )

            return followers
        except Exception as e:
            '''raises the exceptions instead of 500 internal server error'''
            if isinstance(e, UserNotFoundError):
                raise UserNotFoundError()
            elif isinstance(e, FollowersNotFoundError):
                raise FollowersNotFoundError()

            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                'Internal server error occured while retrieving user {id} followers',
                id=user_id,
            )
            raise ServerError() from e

    @staticmethod
    def get_followings(
        current_user: User, username: str, refresh_token: str, db: Session
    ):
        _ = validate_refresh_token(refresh_token, db)

        user_id = current_user.id

        try:
            '''only query db if current user tries to get other user's followings'''
            if current_user.username == username:
                '''get the current user's followings'''
                followings: list[User] | None = user_repo_v1.get_followings(
                    current_user
                )
            else:
                '''get other user's followings'''
                user: User | None = user_repo_v1.get_user_by_username(username, db)

                if not user:
                    sentry_logger.error(
                        'User with username: {username} not found', username=username
                    )
                    raise UserNotFoundError()
                user_id = user.id

                followings: list[User] | None = user_repo_v1.get_followings(user)

            if not followings:
                sentry_logger.error('User {id} followings not found', id=user_id)
                raise FollowingNotFoundError()

            sentry_logger.info(
                'User {id} followings retrieved from database', id=user_id
            )

            return followings
        except Exception as e:
            '''raises the exceptions instead of 500 internal server error'''
            if isinstance(e, UserNotFoundError):
                raise UserNotFoundError()
            elif isinstance(e, FollowingNotFoundError):
                raise FollowingNotFoundError()

            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                'Internal server error occured while retrieving user {id} followings',
                id=user_id,
            )
            raise ServerError() from e

    @staticmethod
    def get_user_posts(
        current_user: User,
        username: str,
        refresh_token: str,
        db: Session,
        created_at: int | None = None,
        sort: str | None = None,
        order: str | None = None,
        offset: int = 0,
        limit: int = 10,
    ) -> list[PostReadV1]:
        _ = validate_refresh_token(refresh_token, db)

        user_id = current_user.id

        try:
            if current_user.username == username:
                '''select all posts made by the current logged in user'''

                posts_db: list = user_repo_v1.get_current_user_posts(
                    user_id, db, created_at, sort, order, offset, limit
                )
            else:
                '''select all posts by the user with the provided username
                that the current logged in user should see that is posts
                set to public and posts set to followers if the current
                logged in user is a follower'''
                user: User | None = user_repo_v1.get_user_by_username(username, db)

                if not user:
                    sentry_logger.error(
                        'User with username {username} not found', username=username
                    )
                    raise UserNotFoundError()
                user_id = user.id

                posts_db: list = user_repo_v1.get_user_posts(
                    current_user,
                    user,
                    user_id,
                    db,
                    created_at,
                    sort,
                    order,
                    offset,
                    limit,
                )

            if not posts_db:
                sentry_logger.error('User {id} posts not found', id=user_id)
                raise PostsNotFoundError()

            user_posts: list[PostReadV1] = []
            for post_db in posts_db:
                (
                    id,
                    title,
                    content,
                    visibility,
                    created_at,
                    display_name,
                    username,
                ) = post_db

                post: Post = post_repo_v1.get_post_by_id(id, db)

                post_read = PostReadV1(
                    id=id,
                    title=title,
                    content=content,
                    visibility=visibility,
                    created_at=created_at,
                    display_name=display_name,
                    username=username,
                    comments=len(post.comments),
                    likes=len(post.likes),
                )
                user_posts.append(post_read)

            sentry_logger.info('User {id} posts retrieved from database', id=user_id)
            return user_posts
        except Exception as e:
            '''raises the exceptions instead of 500 internal server error'''
            if isinstance(e, UserNotFoundError):
                raise UserNotFoundError()
            elif isinstance(e, PostsNotFoundError):
                raise PostsNotFoundError()

            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                'Internal server ocured while retrieving user {id} posts from database',
                id=user_id,
            )
            raise ServerError() from e

    @staticmethod
    def get_liked_post(
        current_user: User,
        username: str,
        refresh_token: str,
        db: Session,
        offset: int = 0,
        limit: int = 10,
    ) -> list[PostReadV1]:
        _ = validate_refresh_token(refresh_token, db)

        user_id = current_user.id

        try:
            '''only query db if current user tries to get other user's liked posts'''
            if current_user.username == username:
                liked_posts: list = user_repo_v1.get_liked_posts(
                    current_user.id, db, offset, limit
                )
            else:
                user: User | None = user_repo_v1.get_user_by_username(username, db)

                if not user:
                    sentry_logger.error(
                        'User with username: {username} not found', username=username
                    )
                    raise UserNotFoundError()
                user_id = user.id

                liked_posts: list = user_repo_v1.get_liked_posts(
                    user.id, db, offset, limit
                )

            if not liked_posts:
                sentry_logger.error('User {id} posts not found', id=user_id)
                raise PostsNotFoundError()

            user_posts: list[PostReadV1] = []
            for post_db in liked_posts:
                (
                    display_name,
                    username,
                    id,
                    title,
                    content,
                    visibility,
                    created_at,
                ) = post_db

                post: Post = post_repo_v1.get_post_by_id(id, db)

                post_read = PostReadV1(
                    id=id,
                    title=title,
                    content=content,
                    visibility=visibility,
                    created_at=created_at,
                    display_name=display_name,
                    username=username,
                    comments=len(post.comments),
                    likes=len(post.likes),
                )
                user_posts.append(post_read)

            sentry_logger.info('User {id} posts retrieved from database', id=user_id)
            return user_posts
        except Exception as e:
            '''raises the exceptions instead of 500 internal server error'''
            if isinstance(e, UserNotFoundError):
                raise UserNotFoundError()
            elif isinstance(e, PostsNotFoundError):
                raise PostsNotFoundError()

            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                'Internal server error occured while retrieving user {id} liked posts',
                id=user_id,
            )
            raise ServerError() from e

    @staticmethod
    def get_user_comments(
        current_user: User,
        username: str,
        refresh_token: str,
        db: Session,
        created_at: int | None = None,
        sort: str | None = None,
        order: str | None = None,
        offset: int = 0,
        limit: int = 10,
    ) -> list[CommentReadV1]:
        _ = validate_refresh_token(refresh_token, db)

        user_id = current_user.id

        try:
            '''only query db if current user tries to get otheruser's followings'''
            if current_user.username == username:
                '''get current user's comments'''
                comments: list = user_repo_v1.get_user_comments(
                    current_user.id, db, created_at, sort, order, offset, limit
                )
            else:
                '''get other user's comments'''
                user: User | None = user_repo_v1.get_user_by_username(username, db)

                if not user:
                    sentry_logger.error(
                        'User with username: {username} not found', username=username
                    )
                    raise UserNotFoundError()
                user_id = user.id

                comments: list = user_repo_v1.get_user_comments(
                    current_user.id, db, created_at, sort, order, offset, limit
                )

            if not comments:
                sentry_logger.error('Comments for User {id} not found', id=user_id)
                raise CommentsNotFoundError()

            user_comments: list[CommentReadV1] = []
            for comment_db in comments:
                comment_id, content, display_name, username, created_at = comment_db
                comment: Comment = post_repo_v1.get_comment_by_id(comment_id, db)
                comment_read = CommentReadV1(
                    id=comment_id,
                    content=content,
                    display_name=display_name,
                    username=username,
                    created_at=created_at,
                    likes=len(comment.comment_likes),
                )
                user_comments.append(comment_read)

            sentry_logger.info('User {id} comments retrieved from database', id=user_id)
            return user_comments
        except Exception as e:
            '''raises the exceptions instead of 500 internal server error'''
            if isinstance(e, UserNotFoundError):
                raise UserNotFoundError()
            elif isinstance(e, CommentsNotFoundError):
                raise CommentsNotFoundError()

            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                'Internal server error occured while retrieving user {id} comments from db',
                id=user_id,
            )
            raise ServerError() from e

    @staticmethod
    async def get_user_avatar(
        current_user: User,
        username: User,
        refresh_token: str,
        image_url: str,
        db: Session,
    ):
        _ = validate_refresh_token(refresh_token, db)

        user_id = current_user.id

        try:
            '''only query db if current user tries to get otheruser's followings'''
            if current_user.username == username:
                '''get current user avatar'''
                url: str | None = user_repo_v1.get_user_avatar(
                    image_url, current_user.id, db
                )
            else:
                '''get other user avatar'''

                user: User | None = user_repo_v1.get_user_by_username(username, db)

                if not user:
                    sentry_logger.error(
                        'User with username: {username} not found', username=username
                    )
                    raise UserNotFoundError()
                user_id = user.id

                url: str | None = user_repo_v1.get_user_avatar(image_url, user.id, db)

            if not url:
                sentry_logger.error('User {id} avatar not found', id=user_id)
                raise AvatarNotFoundError()

            path: Path = Path(settings.PROFILE_IMAGE_PATH).resolve()
            filepath: str = f'{str(path)}\\{url}'

            sentry_logger.info('User {id} avatar retrieved from database', id=user_id)
            return filepath
        except Exception as e:
            '''raises the exceptions instead of 500 internal server error'''
            if isinstance(e, UserNotFoundError):
                raise UserNotFoundError()
            elif isinstance(e, AvatarNotFoundError):
                raise AvatarNotFoundError()

            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                'Internal server error occured while retrieving user {id} avatar from db',
                id=user_id,
            )
            raise ServerError() from e

    @staticmethod
    def add_user(user: User, db: Session):
        '''create and update a user'''
        user_repo_v1.add_user(user, db)

    @staticmethod
    def follow_user(current_user: User, username: str, refresh_token: str, db: Session):
        _ = validate_refresh_token(refresh_token, db)

        user: User = user_repo_v1.get_user_by_username(username, db)

        if not user:
            sentry_logger.error(
                'User not found while attempting to follow {username}',
                username=username,
            )
            raise UserNotFoundError()

        '''ensure idempotency by checking if the current user is already
        following user or simply just return if a user tries to follow themselves'''
        if user in current_user.following or current_user.username == username:
            return

        try:
            user_repo_v1.follow_user(current_user, user, db)
            db.commit()
            sentry_logger.info(
                '{current_user} followed {user} successfully',
                current_user=current_user,
                user=user.username,
            )
        except Exception as e:
            db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                'Internal server error occured while {current_user_id} attempted to follow user {user_id}',
                current_user_id=current_user.id,
                user_id=user.id,
            )
            raise ServerError() from e

    @staticmethod
    def create_role(role_create: RoleCreateV1, db: Session) -> Role:
        role = user_repo_v1.get_role(role_create.name, db)

        if role:
            sentry_logger.error('{name} role exists', name=role_create.name)
            raise RoleExistsError()

        role_db = Role(name=role_create.name)

        try:
            user_repo_v1.create_role(role_db, db)
            db.commit()
            sentry_logger.info('{name} role created', name=role_create.name)
        except Exception as e:
            db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                'Internal server error while creating {name} role',
                name=role_create.name,
            )
            raise ServerError() from e
        finally:
            db.close()

        role_out = user_repo_v1.get_role(role_db.name, db)
        return role_out

    @staticmethod
    async def upload_image(
        refresh_token: str,
        user: User,
        image_uploads: list[UploadFile],
        db: Session,
    ) -> ImageReadV1:
        _ = validate_refresh_token(refresh_token, db)

        # validate file uploaded to ensure an image is uploaded
        for i in image_uploads:
            if not await validate_image(i):
                sentry_logger.error('User {id} uploaded an invalid image', id=user.id)
                raise InvalidImageError()

        # restricts a user from uploading 0 or more than 2 images
        if len(image_uploads) < 1 or len(image_uploads) > 2:
            sentry_logger.error(
                'User {id} uploaded zero or more than two images', id=user.id
            )
            raise ImageUploadError()

        user_images: list[ProfileImage] = user_repo_v1.get_user_images(user)

        # checks if the user already uploaded both avatar and header images
        if len(user_images) >= 2:
            sentry_logger.error('User {id} profile images complete', id=user.id)
            raise ProfileImageExistsError()

        try:
            image_urls: list[str] = []
            for img in image_uploads:
                image_id: UUID = user_repo_v1.get_image_id(img.filename, db)

                # this ensures a duplicate image is not created
                # and the profile image is created directly instead
                # allowing just one type of image on disk and database(images table)
                if image_id:
                    profile_img: ProfileImage = ProfileImage(
                        user_id=user.id, image_id=image_id
                    )

                    user_repo_v1.create_profile_image(profile_img, db)
                else:
                    path: Path = Path(settings.PROFILE_IMAGE_PATH).resolve()
                    file_path: str = f'{str(path)}\\{img.filename}'

                    await write_file(file_path, img)
                    image: Image = Image(
                        image_url=img.filename,
                        image_type=img.content_type,
                        image_size=img.size,
                    )
                    user_repo_v1.create_image(user, image, db)
                image_urls.append(img.filename)

            db.commit()
            profile_images: ImageReadV1 = ImageReadV1(image_url=image_urls)
            sentry_logger.info('User {id} profile image uploaded', id=user.id)
            return profile_images
        except Exception as e:
            db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                'Internal server error while uploading user {id} profile image',
                id=user.id,
            )
            raise ServerError() from e

    @staticmethod
    def update_user(
        user_update: UserUpdateV1, user: User, refresh_token: str, db: Session
    ) -> User:
        _ = validate_refresh_token(refresh_token, db)

        if user_update.email and user_repo_v1.get_user_by_email(user_update.email, db):
            sentry_logger.error(
                'User with email {email} exists', email=user_update.email
            )
            raise UserExistsError()

        if user_update.username and user_repo_v1.get_user_by_username(
            user_update.username, db
        ):
            sentry_logger.error(
                'User with username {username} exists',
                email=user_update.username,
            )
            raise UserExistsError()

        user_update_dict: dict = user_update.model_dump(exclude_unset=True)

        for k, v in user_update_dict.items():
            setattr(user, k, v)

        try:
            user_repo_v1.add_user(user, db)
            sentry_logger.info('User {id} profile updated', id=user.id)
            db.commit()
        except Exception as e:
            db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                'Internal server error occured while updating user {id} profile',
                id=user.id,
            )
            raise ServerError() from e

        return user_repo_v1.get_user_by_id(user.id, db)

    @staticmethod
    def unfollow_user(
        current_user: User, username: str, refresh_token: str, db: Session
    ):
        _ = validate_refresh_token(refresh_token, db)

        user: User = user_repo_v1.get_user_by_username(username, db)

        if not user:
            sentry_logger.error(
                'User not found while attempting to follow {username}',
                username=username,
            )
            raise UserNotFoundError()

        if current_user.username == username or user not in current_user.following:
            return

        try:
            user_repo_v1.unfollow_user(current_user, user, db)
            db.commit()
            sentry_logger.info(
                '{current_user} unfollowed {user} successfully',
                current_user=current_user,
                user=user.username,
            )
        except Exception as e:
            db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                'Internal server error occured while user {current_user_id} attempted to unfollow user {user_id}',
                current_user_id=current_user.id,
                user_id=user.id,
            )
            raise ServerError() from e

    @staticmethod
    def delete_user_accounts(db: Session):
        '''deletes user accounts 30 days after deactivation'''
        try:
            user_repo_v1.delete_user(db)
            db.commit()
            sentry_logger.info('User accounts deleted permanently')
        except Exception as e:
            db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                'Internal server error while deleting user accounts permanently'
            )
            raise ServerError() from e
        finally:
            db.close()

    @staticmethod
    def delete_profile_image(
        user: User, image_url: str, refresh_token: str, db: Session
    ):
        _ = validate_refresh_token(refresh_token, db)

        profile_image: ProfileImage | None = user_repo_v1.get_profile_image(
            image_url, user.id, db
        )

        if not profile_image:
            sentry_logger.error(
                'Image not found with url {image_url} for user {id}',
                image_url=image_url,
                id=user.id,
            )
            raise AvatarNotFoundError()

        try:
            user_repo_v1.delete_profile_image(profile_image, db)
            db.commit()
            path: Path = Path(settings.PROFILE_IMAGE_PATH).resolve()
            file_path: str = f'{str(path)}\\{image_url}'

            if os.path.exists():
                os.remove(file_path)

            sentry_logger.info('Profile image deleted')
        except Exception as e:
            db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error('Internal server error while deleting profile image')
            raise ServerError() from e


user_service_v1 = UserServiceV1()
