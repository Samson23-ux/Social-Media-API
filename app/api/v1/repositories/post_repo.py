from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, desc, func, or_, case

from app.models.users import User
from app.models.users import follows
from app.models.images import Image, PostImage
from app.api.v1.schemas.posts import VisibilityEnum
from app.models.posts import Post, Comment, Like, CommentLike


class PostRepoV1:
    @staticmethod
    def get_feed_posts(
        user_id: UUID,
        db: Session,
        offset: int = 0,
        limit: int = 10,
    ) -> list:
        '''select all user's posts and post made by other users
        with public or followers'''
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
            .join(User, Post.user_id == User.id)
            .join(
                follows,
                or_(
                    and_(
                        Post.user_id == follows.c.following_id,
                        user_id == follows.c.follower_id,
                    ),
                    Post.visibility != VisibilityEnum.FOLLOWERS,
                    Post.user_id == user_id,
                ),
            )
            .where(Post.visibility != VisibilityEnum.PRIVATE)
        )

        stmt = stmt.offset(offset).limit(limit)
        feed_posts: list = db.execute(stmt).all()
        return feed_posts

    @staticmethod
    def get_search_posts(
        user_id: UUID,
        db: Session,
        q: str,
        created_at: int | None = None,
        sort: str | None = None,
        order: str | None = None,
        offset: int = 0,
        limit: int = 10,
    ) -> list:
        sortable_fields: list = ['created_at', 'likes']
        query_vector = func.websearch_to_tsquery('english', q)
        vector_rank = func.ts_rank(Post.content_search, query_vector).label(
            'vector_rank'
        )

        # a combination of both pg_trgms and FTS is used to search for posts
        stmt = (
            select(
                Post.id,
                Post.title,
                Post.content,
                Post.visibility,
                Post.created_at,
                User.display_name,
                User.username,
                vector_rank,
            )
            .join(User, Post.user_id == User.id)
            .join(
                follows,
                or_(
                    and_(
                        Post.user_id == follows.c.following_id,
                        user_id == follows.c.follower_id,
                    ),
                    Post.visibility != VisibilityEnum.FOLLOWERS,
                    Post.user_id == user_id,
                ),
            )
            .where(
                and_(
                    Post.visibility != VisibilityEnum.PRIVATE,
                    or_(
                        Post.content_search.op('@@')(query_vector), Post.title.ilike(q)
                    ),
                )
            )
        )

        if created_at:
            stmt = stmt.where(Post.created_at == created_at)

        stmt = (
            stmt.select(
                case(
                    (Comment.post_id.is_(None), 0),
                    else_=func.count(Comment.user_id),
                ).label('comments'),
                case(
                    (Like.post_id.is_(None), 0),
                    else_=func.count(Like.user_id),
                ).label('likes')
            )
            .outerjoin(Like, Post.id == Like.post_id)
            .group_by(Like.post_id)
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

        stmt = stmt.offset(offset).limit(limit)
        search_posts: list = db.execute(stmt).all()
        return search_posts

    @staticmethod
    def get_following_posts(
        user_id: UUID,
        db: Session,
        offset: int = 0,
        limit: int = 10,
    ) -> list[Post]:
        stmt = (
            select(Post)
            .join(
                follows,
                and_(
                    Post.user_id == follows.c.following_id,
                    user_id == follows.c.follower_id,
                ),
            )
            .where(Post.visibility != VisibilityEnum.PRIVATE)
        )

        stmt = stmt.offset(offset).limit(limit)
        following_posts: list[Post] = db.execute(stmt).scalars()
        return following_posts

    @staticmethod
    def get_post_by_id(post_id: UUID, db: Session) -> Post | None:
        stmt = select(Post).where(Post.id == post_id)
        post: Post | None = db.execute(stmt).scalar()
        return post

    @staticmethod
    def get_image(image_url: str, db: Session):
        stmt = select(Image).where(Image.url == image_url)
        image: Image = db.execute(stmt).scalar()
        return image

    @staticmethod
    def get_comment_by_id(comment_id: UUID, db: Session) -> Comment | None:
        stmt = select(Comment).where(Comment.id == comment_id)
        comment: Comment | None = db.execute(stmt).scalar()
        return comment

    @staticmethod
    def get_like(user_id: UUID, post_id: UUID, db: Session) -> Like | None:
        stmt = select(Like).where(
            and_(Like.user_id == user_id, Like.post_id == post_id)
        )
        like: Like | None = db.execute(stmt).scalar()
        return like

    @staticmethod
    def get_comment_like(
        user_id: UUID, comment_id: UUID, db: Session
    ) -> CommentLike | None:
        stmt = select(CommentLike).where(
            and_(CommentLike.user_id == user_id, CommentLike.comment_id == comment_id)
        )
        comment_like: CommentLike | None = db.execute(stmt).scalar()
        return comment_like

    @staticmethod
    def get_post_comments(
        post_id: UUID,
        db: Session,
        sort: str | None = None,
        order: str | None = None,
        offset: int = 0,
        limit: int = 10,
    ) -> list:
        sortable_fields: list = ['created_at', 'likes']
        stmt = select(Comment.id, Comment.content, Comment.created_at).join(
            Post, post_id == Comment.post_id
        )

        stmt = (
            stmt.select(
                case(
                    (CommentLike.comment_id.is_(None), 0),
                    else_=func.count(CommentLike.user_id),
                ).label('likes')
            )
            .outerjoin(CommentLike, Comment.id == CommentLike.comment_id)
            .group_by(CommentLike.comment_id)
        )

        if sort not in sortable_fields or sort == 'created_at':
            if order == 'desc':
                stmt = stmt.order_by(desc(Comment.created_at))
            else:
                stmt = stmt.order_by(Comment.created_at)
        elif sort == 'likes':
            if order == 'desc':
                stmt = stmt.order_by(desc('likes'))
            else:
                stmt = stmt.order_by('likes')

        stmt = stmt.offset(offset).limit(limit)
        post_comments: list = db.execute(stmt).all()
        return post_comments

    @staticmethod
    def add_post(post: Post, db: Session):
        '''create and update post'''
        db.add(post)
        db.flush()
        db.refresh(post)

    @staticmethod
    def create_image(post: Post, image: Image, db: Session):
        post.images.append(image)
        db.flush()
        db.refresh(image)

    @staticmethod
    def create_post_image(post_image: PostImage, db: Session):
        db.add(post_image)
        db.flush()
        db.refresh(post_image)

    @staticmethod
    def like_post(like: Like, db: Session):
        db.add(like)
        db.flush()
        db.refresh(like)

    @staticmethod
    def like_comment(comment_like: CommentLike, db: Session):
        db.add(comment_like)
        db.flush()
        db.refresh(comment_like)

    @staticmethod
    def create_comment(comment: Comment, db: Session):
        db.add(comment)
        db.flush()
        db.refresh(comment)

    @staticmethod
    def delete_post(post: Post, db: Session):
        db.delete(post)
        db.flush()

    @staticmethod
    def unlike_post(post: Post, like: Like, db: Session):
        post.likes.remove(like)
        db.flush()

    @staticmethod
    def unlike_comment(comment: Comment, comment_like: CommentLike, db: Session):
        comment.comment_likes.remove(comment_like)
        db.flush()

    @staticmethod
    def delete_comment(comment: Comment, db: Session):
        db.delete(comment)
        db.flush()


post_repo_v1 = PostRepoV1()
