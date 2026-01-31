from pathlib import Path
import sentry_sdk
from uuid import UUID
from fastapi import UploadFile
from sqlalchemy.orm import Session
from sentry_sdk import logger as sentry_logger

from app.models.users import User
from app.core.config import settings
from app.core.exceptions import ServerError
from app.models.images import Image, PostImage
from app.utils import write_file, validate_image
from app.api.v1.schemas.images import ImageReadV1
from app.core.security import validate_refresh_token
from app.api.v1.repositories.post_repo import post_repo_v1
from app.models.posts import Post, Comment, Like, CommentLike
from app.core.exceptions import (
    PostUploadError,
    PostNotFoundError,
    InvalidImageError,
    PostsNotFoundError,
    AuthorizationError,
    CommentNotFoundError,
    CommentsNotFoundError,
    PostImageNotFoundError,
)
from app.api.v1.schemas.posts import (
    PostReadV1,
    PostUpdateV1,
    PostCreateV1,
    CommentReadV1,
    PostReadBaseV1,
    CommentCreateV1,
    CommentReadBaseV1,
)


class PostServiceV1:
    @staticmethod
    def get_feed_posts(
        user: User,
        refresh_token: str,
        db: Session,
        offset: int = 0,
        limit: int = 10,
    ) -> list[PostReadV1]:
        _ = validate_refresh_token(refresh_token, db)

        try:
            posts_db: list = post_repo_v1.get_feed_posts(user.id, db, offset, limit)

            if not posts_db:
                sentry_logger.error('No posts found in database')
                raise PostsNotFoundError()

            feed_posts: list[PostReadV1] = []
            for post_db in posts_db:
                (id, title, content, visibility, created_at, display_name, username) = (
                    post_db
                )

                post_db: Post = post_repo_v1.get_post_by_id(id, db)

                post_read = PostReadV1(
                    id=id,
                    title=title,
                    content=content,
                    visibility=visibility,
                    created_at=created_at,
                    display_name=display_name,
                    username=username,
                    comments=len(post_db.comments),
                    likes=len(post_db.likes),
                )
                feed_posts.append(post_read)

            sentry_logger.info('Posts retrieved from database')
            return feed_posts
        except Exception as e:
            if isinstance(e, PostsNotFoundError):
                raise PostsNotFoundError()

            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                'Internal server error occured while retrieving feed posts from database'
            )
            raise ServerError() from e

    @staticmethod
    def get_search_posts(
        user: User,
        refresh_token: str,
        db: Session,
        q: str,
        sort: str | None = None,
        order: str | None = None,
        offset: int = 0,
        limit: int = 10,
    ) -> list[PostReadV1]:
        _ = validate_refresh_token(refresh_token, db)

        try:
            posts_db: list = post_repo_v1.get_search_posts(
                user.id, db, q, sort, order, offset, limit
            )

            if not posts_db:
                sentry_logger.error('No posts found in database')
                raise PostsNotFoundError()

            search_posts: list[PostReadV1] = []
            for post_db in posts_db:
                (
                    id,
                    title,
                    content,
                    visibility,
                    created_at,
                    display_name,
                    username,
                    vector_rank,
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
                search_posts.append(post_read)

            sentry_logger.info('Posts retrieved from database')
            return search_posts
        except Exception as e:
            if isinstance(e, PostsNotFoundError):
                raise PostsNotFoundError()

            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                'Internal server error occured while retrieving feed posts from database'
            )
            raise ServerError() from e

    @staticmethod
    def get_following_posts(
        user: User,
        refresh_token: str,
        db: Session,
        offset: int = 0,
        limit: int = 10,
    ) -> list[PostReadV1]:
        '''get posts made by following users'''
        _ = validate_refresh_token(refresh_token, db)

        try:
            posts_db: Post = post_repo_v1.get_following_posts(
                user.id, db, offset, limit
            )

            if not posts_db:
                raise PostsNotFoundError()

            posts: list[PostReadV1] = []
            for post_db in posts_db:
                (
                    id,
                    title,
                    content,
                    visibility,
                    created_at,
                    display_name,
                    username
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
                posts.append(post_read)
            sentry_logger.info('Following posts retrieved from database')
            return posts
        except Exception as e:
            if isinstance(e, PostsNotFoundError):
                raise PostsNotFoundError()

            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                'Internal server error occured while retrieving posts from database'
            )
            raise ServerError() from e

    @staticmethod
    def get_post_comments(
        user: User,
        post_id: UUID,
        refresh_token: str,
        db: Session,
        sort: str | None = None,
        order: str | None = None,
        offset: int = 0,
        limit: int = 10,
    ) -> list[CommentReadV1]:
        _ = validate_refresh_token(refresh_token, db)

        post_db: Post = post_repo_v1.get_post_by_id(post_id, db)

        if not post_db:
            sentry_logger.error('Post {id} not found', id=post_id)
            raise PostNotFoundError()

        try:
            post_comments_db: list = post_repo_v1.get_post_comments(
                post_id, db, sort, order, offset, limit
            )

            if not post_comments_db:
                sentry_logger.error('No comments found for post {id}', id=post_id)
                raise CommentsNotFoundError()

            post_comments: list[CommentReadV1] = []
            for post_comment in post_comments_db:
                comment_id, comment_content, comment_created_at, comment_likes = (
                    post_comment
                )
                comment: CommentReadV1 = CommentReadV1(
                    id=comment_id,
                    content=comment_content,
                    created_at=comment_created_at,
                    display_name=user.display_name,
                    username=user.username,
                    likes=comment_likes,
                )
                post_comments.append(comment)
            sentry_logger.info('Post {id} retrieved from database', id=post_id)
            return post_comments
        except Exception as e:
            if isinstance(e, CommentsNotFoundError):
                raise CommentsNotFoundError()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                'Internal server error occured while retrieving post {id} comments from database',
                id=post_id,
            )
            raise ServerError() from e

    @staticmethod
    def get_post_by_id(post_id: UUID, refresh_token: str, db: Session) -> PostReadV1:
        _ = validate_refresh_token(refresh_token, db)

        post_db: Post = post_repo_v1.get_post_by_id(post_id, db)

        if not post_db:
            sentry_logger.error('Post {id} not found', id=post_id)
            raise PostNotFoundError()

        user: User = post_db.user

        try:
            post: PostReadV1 = PostReadV1(
                **PostReadBaseV1.model_validate(post_db).model_dump(),
                display_name=user.display_name,
                username=user.username,
                likes=len(post_db.likes),
                comments=len(post_db.comments),
            )
            sentry_logger.info('Post {id} retrieved from database', id=post_id)
            return post
        except Exception as e:
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                'Internal server error occured while retrieving post {id} from database',
                id=post_id,
            )
            raise ServerError() from e

    @staticmethod
    def get_post_image(
        user: User, post_id: UUID, image_url: str, refresh_token: str, db: Session
    ):
        _ = validate_refresh_token(refresh_token, db)

        post_db: Post = post_repo_v1.get_post_by_id(post_id, db)

        if not post_db:
            sentry_logger.error('Post {id} not found', id=post_id)
            raise PostNotFoundError()

        try:
            image_db: Image = post_repo_v1.get_image(image_url, db)

            if not image_db:
                sentry_logger.error(
                    'Post image not found for image url {url}', url=image_url
                )
                raise PostImageNotFoundError()

            image_path = Path(settings.POST_IMAGE_PATH).resolve()
            image_url: str = f'{image_path}\\{image_url}'
            return image_url
        except Exception as e:
            if isinstance(e, PostImageNotFoundError):
                raise PostImageNotFoundError()

            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                'Internal server error occured while retrieving image {url} from database',
                url=image_url,
            )
            raise ServerError() from e

    @staticmethod
    def get_post_comment(
        post_id: UUID, comment_id: UUID, refresh_token: str, db: Session
    ) -> CommentReadV1:
        _ = validate_refresh_token(refresh_token, db)

        post_db: Post | None = post_repo_v1.get_post_by_id(post_id, db)

        if not post_db:
            sentry_logger.error('Post {id} not found', id=post_id)
            raise PostNotFoundError()

        comment_db: Comment | None = post_repo_v1.get_comment_by_id(comment_id, db)

        if not comment_db:
            sentry_logger.error('Comment {id} not found', id=comment_id)
            raise CommentNotFoundError()

        user: User = post_db.user

        try:
            comment: CommentReadV1 = CommentReadV1(
                **CommentReadBaseV1.model_validate(comment_db).model_dump(),
                display_name=user.display_name,
                username=user.username,
                likes=len(comment_db.comment_likes),
            )
            sentry_logger.info('Post {id} comment retrieved from database', id=post_id)
            return comment
        except Exception as e:
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                'Internal server error occured while retrieving a comment from post {id} from database',
                id=post_id,
            )
            raise ServerError() from e

    @staticmethod
    def create_post(
        post_create: PostCreateV1, user: User, refresh_token: str, db: Session
    ) -> PostReadV1:
        _ = validate_refresh_token(refresh_token, db)

        post_db: Post = Post(**post_create.model_dump(), user_id=user.id)

        try:
            post_repo_v1.add_post(post_db, db)
            db.commit()
            sentry_logger.info('User {id} post created', id=user.id)
            post_db_out: Post = post_repo_v1.get_post_by_id(post_db.id, db)
            post: PostReadV1 = PostReadV1(
                **PostReadBaseV1.model_validate(post_db_out).model_dump(),
                display_name=user.display_name,
                username=user.username,
            )
            return post
        except Exception as e:
            db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                'Internal server error while writing user {id} post to database',
                id=user.id,
            )
            raise ServerError() from e

    @staticmethod
    def create_comment(
        post_id: UUID,
        comment_create: CommentCreateV1,
        user: User,
        refresh_token: str,
        db: Session,
    ) -> CommentReadV1:
        _ = validate_refresh_token(refresh_token, db)

        post_db: Post = post_repo_v1.get_post_by_id(post_id, db)

        if not post_db:
            sentry_logger.error('Post {id} not found', id=post_id)
            raise PostNotFoundError()

        try:
            comment_db: Comment = Comment(
                **comment_create.model_dump(), post_id=post_id, user_id=user.id
            )
            post_repo_v1.create_comment(comment_db, db)
            db.commit()
            comment_db_out: Comment = post_repo_v1.get_comment_by_id(comment_db.id, db)

            comment: CommentReadV1 = CommentReadV1(
                **CommentReadBaseV1.model_validate(comment_db_out).model_dump(),
                display_name=user.display_name,
                username=user.username,
                likes=len(comment_db_out.comment_likes),
            )
            sentry_logger.info('Comment {id} created', id=comment.id)
            return comment
        except Exception as e:
            db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                'Internal server error occured while writing user {id} comment to database',
                username=user.id,
            )
            raise ServerError() from e

    @staticmethod
    async def upload_image(
        user: User,
        post_id: UUID,
        image_uploads: list[UploadFile],
        refresh_token: str,
        db: Session,
    ):
        _ = validate_refresh_token(refresh_token, db)

        # validate file uploaded to ensure an image is uploaded
        for i in image_uploads:
            if not await validate_image(i):
                sentry_logger.error('User {id} uploaded an invalid image', id=user.id)
                raise InvalidImageError()

        # restricts a user from uploading 0 or more than 2 images
        if len(image_uploads) < 1:
            sentry_logger.error(
                'User {id} uploaded zero images', id=user.id
            )
            raise PostUploadError()

        post_db: Post = post_repo_v1.get_post_by_id(post_id, db)

        if not post_db:
            sentry_logger.error('Post {id} not found', id=post_id)
            raise PostNotFoundError()

        image_urls: list[str] = []
        try:
            for image in image_uploads:
                '''prevent duplicate image uploads if it already exists in database
                and has been written to disk even by another user forcing reference
                to the same image'''
                image_db: Image = post_repo_v1.get_image(image.filename, db)
                if image_db:
                    '''create post image'''
                    post_image: PostImage = PostImage(
                        post_id=post_id, image_id=image_db.id
                    )
                    post_repo_v1.create_post_image(post_image, db)
                else:
                    '''create image and post image'''
                    image_path = Path(settings.POST_IMAGE_PATH).resolve()
                    filepath: str = f'{str(image_path)}\\{image.filename}'
                    await write_file(filepath, image)

                    image_db: Image = Image(
                        image_url=image.filename,
                        image_type=image.content_type,
                        image_size=image.size,
                    )
                    post_repo_v1.create_image(post_db, image_db, db)

                image_urls.append(image.filename)

            db.commit()
            post_images: ImageReadV1 = ImageReadV1(image_url=image_urls)
            sentry_logger.info('User {id} post images uploaded', id=user.id)
            return post_images
        except Exception as e:
            db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                'Internal server error occured while uploading user {id} post images',
                username=user.id,
            )
            raise ServerError() from e

    @staticmethod
    def like_post(user: User, post_id: UUID, refresh_token: str, db: Session):
        _ = validate_refresh_token(refresh_token, db)

        post_db: Post = post_repo_v1.get_post_by_id(post_id, db)

        if not post_db:
            sentry_logger.error('Post {id} not found', id=post_id)
            raise PostNotFoundError()
        
        # prevents double likes from increasing post likes count
        if post_repo_v1.get_like(user.id, post_id, db):
            return

        try:
            like: Like = Like(user_id=user.id, post_id=post_id)
            post_repo_v1.like_post(like, db)
            db.commit()
            sentry_logger.info(
                'Post {id} liked by user {id}', id=post_id, username=user.id
            )
        except Exception as e:
            db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                'Internal server error occured while liking post {id}', id=post_id
            )
            raise ServerError() from e

    @staticmethod
    def like_comment(
        user: User,
        post_id: UUID,
        comment_id: UUID,
        refresh_token: str,
        db: Session,
    ):
        _ = validate_refresh_token(refresh_token, db)

        post_db: Post = post_repo_v1.get_post_by_id(post_id, db)

        if not post_db:
            sentry_logger.error('Post {id} not found', id=post_id)
            raise PostNotFoundError()

        comment_db: Comment | None = post_repo_v1.get_comment_by_id(comment_id, db)

        if not comment_db:
            sentry_logger.error('Comment {id} not found', id=comment_id)
            raise CommentNotFoundError()

        # prevents double likes from increasing comment likes count
        if post_repo_v1.get_comment_like(user.id, comment_id, db):
            return

        try:
            like: CommentLike = CommentLike(user_id=user.id, comment_id=comment_id)
            post_repo_v1.like_comment(like, db)
            db.commit()
            sentry_logger.info(
                'Comment {id} liked by {username}',
                id=comment_id,
                username=user.username,
            )
        except Exception as e:
            print(e)
            db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                'Internal server error occured while liking comment {id}', id=comment_id
            )
            raise ServerError() from e

    @staticmethod
    def update_post(
        user: User,
        post_id: UUID,
        post_update: PostUpdateV1,
        refresh_token: str,
        db: Session,
    ):
        _ = validate_refresh_token(refresh_token, db)

        post_db: Post = post_repo_v1.get_post_by_id(post_id, db)

        if not post_db:
            sentry_logger.error('Post {id} not found', id=post_id)
            raise PostNotFoundError()

        if post_db.user_id != user.id:
            raise AuthorizationError()

        try:
            post_update_dict: dict = post_update.model_dump(exclude_unset=True)

            for k, v in post_update_dict.items():
                setattr(post_db, k, v)
            post_repo_v1.add_post(post_db, db)
            db.commit()
            sentry_logger.error('Post {id} updated', id=post_id)
            post: Post = post_repo_v1.get_post_by_id(post_id, db)
            post_read: PostReadV1 = PostReadV1(
                **PostReadBaseV1.model_validate(post).model_dump(),
                display_name=user.display_name,
                username=user.username,
                likes=len(post.likes),
            )
            return post_read
        except Exception as e:
            db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                'Internal server error occured while updating post {id}',
                id=post_id,
            )
            raise ServerError() from e

    @staticmethod
    def unlike_post(user: User, post_id: UUID, refresh_token: str, db: Session):
        _ = validate_refresh_token(refresh_token, db)

        post_db: Post = post_repo_v1.get_post_by_id(post_id, db)

        if not post_db:
            sentry_logger.error('Post {id} not found', id=post_id)
            raise PostNotFoundError()
        
        like: Like | None = post_repo_v1.get_like(user.id, post_id, db)
        
        # prevents user from unliking post twice
        if not like:
            return

        try:
            post_repo_v1.unlike_post(post_db, like, db)
            db.commit()
            sentry_logger.info(
                'Post {id} unliked by user {id}', id=post_id, username=user.id
            )
        except Exception as e:
            db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                'Internal server error occured while unliking post {id}', id=post_id
            )
            raise ServerError() from e

    @staticmethod
    def unlike_comment(
        user: User,
        post_id: UUID,
        comment_id: UUID,
        refresh_token: str,
        db: Session,
    ):
        _ = validate_refresh_token(refresh_token, db)
        comment_like: CommentLike | None = post_repo_v1.get_comment_like(
            user.id, comment_id, db
        )

        post_db: Post = post_repo_v1.get_post_by_id(post_id, db)

        if not post_db:
            sentry_logger.error('Post {id} not found', id=post_id)
            raise PostNotFoundError()

        comment_db: Comment | None = post_repo_v1.get_comment_by_id(comment_id, db)

        if not comment_db:
            sentry_logger.error('Comment {id} not found', id=comment_id)
            raise CommentNotFoundError()
        
        # prevents user from unliking comment twice
        if not comment_like:
            return

        try:
            post_repo_v1.unlike_comment(comment_db, comment_like, db)
            db.commit()
            sentry_logger.info(
                'Comment {id} unliked by user {id}',
                id=comment_id,
                username=user.id,
            )
        except Exception as e:
            db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                'Internal server error occured while unliking post {id}', id=post_id
            )
            raise ServerError() from e

    @staticmethod
    def delete_post(post_id: UUID, user: User, refresh_token: str, db: Session):
        _ = validate_refresh_token(refresh_token, db)

        post_db: Post = post_repo_v1.get_post_by_id(post_id, db)

        if not post_db:
            sentry_logger.error('Post {id} not found', id=post_id)
            raise PostNotFoundError()

        try:
            post_repo_v1.delete_post(post_db, db)
            db.commit()
            sentry_logger.info('Post {id} deleted from database', id=post_id)
        except Exception as e:
            db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                'Internal server error occured while deleting post {id} from database',
                id=post_id,
            )
            raise ServerError() from e

    @staticmethod
    def delete_comment(post_id: UUID ,comment_id: UUID, refresh_token: str, db: Session):
        _ = validate_refresh_token(refresh_token, db)

        post_db: Post = post_repo_v1.get_post_by_id(post_id, db)

        if not post_db:
            sentry_logger.error('Post {id} not found', id=post_id)
            raise PostNotFoundError()

        comment_db: Comment = post_repo_v1.get_comment_by_id(comment_id, db)

        if not comment_db:
            sentry_logger.error('Comment {id} not found', id=comment_id)
            raise CommentNotFoundError()

        try:
            post_repo_v1.delete_comment(comment_db, db)
            db.commit()
            sentry_logger.info('Comment {id} deleted from database', id=comment_id)
        except Exception as e:
            db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                'Internal server error occured while deleting comment {id} from database',
                id=comment_id,
            )
            raise ServerError() from e

    @staticmethod
    def delete_post_image(
        post_id: UUID, image_url: str, refresh_token: str, db: Session
    ):
        _ = validate_refresh_token(refresh_token, db)

        post_image: PostImage | None = post_repo_v1.get_post_image(
            image_url, post_id, db
        )

        if not post_image:
            sentry_logger.error(
                'Image not found with url {image_url} for post {id}',
                image_url=image_url,
                id=post_id,
            )
            raise PostImageNotFoundError()

        try:
            post_repo_v1.delete_post_image(post_image, db)
            db.commit()
            sentry_logger.info('Post image deleted')
        except Exception as e:
            db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error('Internal server error while deleting post image')
            raise ServerError() from e


post_service_v1 = PostServiceV1()
