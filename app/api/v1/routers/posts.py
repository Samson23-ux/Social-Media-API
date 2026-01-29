from uuid import UUID
from sqlalchemy.orm import Session
from fastapi.requests import Request
from fastapi.responses import FileResponse
from fastapi import APIRouter, Depends, Query, File, UploadFile

from app.models.users import User
from app.api.v1.schemas.users import UserRole
from app.api.v1.schemas.images import ImageReadV1
from app.api.v1.services.post_service import post_service_v1
from app.dependencies import get_current_user, get_db, required_roles
from app.api.v1.schemas.posts import (
    PostReadV1,
    PostCreateV1,
    PostUpdateV1,
    CommentReadV1,
    PostResponseV1,
    CommentCreateV1,
    CommentResponseV1,
)


post_router_v1 = APIRouter()


# return post by current user and post by users(public and followers visibility)
@post_router_v1.get(
    '/posts/feed/',
    status_code=200,
    response_model=PostResponseV1,
    description='Get feed posts',
)
async def get_feed_posts(
    request: Request,
    offset: int = Query(default=0),
    limit: int = Query(default=10),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    refresh_token: str | None = request.cookies.get('refresh_token')
    feed_posts: list[PostReadV1] = post_service_v1.get_feed_posts(
        user, refresh_token, db, offset, limit
    )
    return PostResponseV1(message='Posts retrieved successfully', data=feed_posts)


@post_router_v1.get(
    '/posts/following/',
    status_code=200,
    response_model=PostResponseV1,
    description='Get posts created by following',
)
async def get_following_posts(
    request: Request,
    offset: int = Query(default=0),
    limit: int = Query(default=10),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    refresh_token: str | None = request.cookies.get('refresh_token')
    posts: list[PostReadV1] = post_service_v1.get_following_posts(
        user, refresh_token, db, offset, limit
    )
    return PostResponseV1(message='Posts retrieved successfully', data=posts)


@post_router_v1.get(
    '/posts/search/',
    status_code=200,
    response_model=PostResponseV1,
    description='Get searched posts',
)
async def get_search_posts(
    request: Request,
    q: str = Query(..., description='Search posts by title or using words in contents'),
    created_at: int = Query(default=None, description='Filter by year created'),
    sort: str = Query(default=None, description='Sort by likes or created_at'),
    order: str = Query(default=None, description='Sort in asc or desc order'),
    offset: int = Query(default=0),
    limit: int = Query(default=10),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    refresh_token: str | None = request.cookies.get('refresh_token')
    search_posts: list[PostReadV1] = post_service_v1.get_search_posts(
        user, refresh_token, db, q, created_at, sort, order, offset, limit
    )
    return PostResponseV1(message='Posts retrieved successfully', data=search_posts)


@post_router_v1.get(
    '/posts/{post_id}/',
    status_code=200,
    response_model=PostResponseV1,
    description='Get a post',
)
async def get_post_by_id(
    post_id: UUID,
    request: Request,
    _=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    refresh_token: str | None = request.cookies.get('refresh_token')
    post: PostReadV1 = post_service_v1.get_post_by_id(post_id, refresh_token, db)
    return PostResponseV1(message='Post retrieved successfully', data=post)


@post_router_v1.get(
    '/posts/{post_id}/images/{image_url}/',
    status_code=200,
    response_class=FileResponse,
    description='Get post image',
)
async def get_post_image(
    post_id: UUID,
    image_url: str,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    refresh_token: str | None = request.cookies.get('refresh_token')
    post_image: str = post_service_v1.get_post_image(
        user, post_id, image_url, refresh_token, db
    )
    return FileResponse(path=post_image)

@post_router_v1.get(
    '/posts/{post_id}/comments/',
    status_code=200,
    response_model=CommentResponseV1,
    description='Get all comments from a post',
)
async def get_post_comments(
    post_id: UUID,
    request: Request,
    sort: str = Query(default=None, description='Sort by likes or created_at'),
    order: str = Query(default=None, description='Sort in asc or desc order'),
    offset: int = Query(default=0),
    limit: int = Query(default=10),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    refresh_token: str | None = request.cookies.get('refresh_token')
    post_coments: list[CommentReadV1] = post_service_v1.get_post_comments(
        user, post_id, refresh_token, db, sort, order, offset, limit
    )
    return CommentResponseV1(
        message='Comments retrieved successfully', data=post_coments
    )


@post_router_v1.get(
    '/posts/{post_id}/comments/{comment_id}/',
    status_code=200,
    response_model=CommentResponseV1,
    description='Get a comment from a post',
)
async def get_comment(
    post_id: UUID,
    comment_id: UUID,
    request: Request,
    _=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    refresh_token: str | None = request.cookies.get('refresh_token')
    comment: CommentReadV1 = post_service_v1.get_post_comment(
        post_id, comment_id, refresh_token, db
    )
    return CommentResponseV1(message='Comment retrieved successfully', data=comment)


@post_router_v1.post(
    '/posts/',
    status_code=201,
    response_model=PostResponseV1,
    description='Create a post',
)
async def create_post(
    request: Request,
    post_create: PostCreateV1,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    refresh_token: str | None = request.cookies.get('refresh_token')
    post: PostReadV1 = post_service_v1.create_post(post_create, user, refresh_token, db)
    return PostResponseV1(message='Post created successfully', data=post)


@post_router_v1.post(
    '/posts/{post_id}/images/',
    status_code=201,
    response_model=ImageReadV1,
    description='Upload post images',
)
async def create_post_image(
    post_id: UUID,
    request: Request,
    post_images: UploadFile = File(
        ..., description='Upload at least 0 and at most 2 post image'
    ),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    refresh_token: str | None = request.cookies.get('refresh_token')
    post_images: ImageReadV1 = post_service_v1.upload_image(
        user, post_id, post_images, refresh_token, db
    )
    return ImageReadV1(message='Post images uploaded successfully', data=post_images)


@post_router_v1.post(
    '/posts/{post_id}/comments/',
    status_code=201,
    response_model=CommentResponseV1,
    description='Comment on a post',
)
async def create_comment(
    post_id: UUID,
    request: Request,
    comment_create: CommentCreateV1,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    refresh_token: str | None = request.cookies.get('refresh_token')
    comment: CommentReadV1 = post_service_v1.create_comment(
        post_id, comment_create, user, refresh_token, db
    )
    return PostResponseV1(message='Comment created successfully', data=comment)


@post_router_v1.patch(
    '/posts/{post_id}/',
    status_code=200,
    response_model=PostResponseV1,
    description='Update post',
)
async def update_post(
    post_id: UUID,
    request: Request,
    post_update: PostUpdateV1,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    refresh_token: str | None = request.cookies.get('refresh_token')
    post: PostReadV1 | None = post_service_v1.update_post(
        user, post_id, post_update, refresh_token, db
    )
    return PostResponseV1(message='Post updated successfully', data=post)


@post_router_v1.patch(
    '/posts/{post_id}/like/',
    status_code=200,
    response_model=PostResponseV1,
    description='Like a post',
)
async def like_post(
    post_id: UUID,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    refresh_token: str | None = request.cookies.get('refresh_token')
    post_service_v1.like_post(user, post_id, refresh_token, db)
    return PostResponseV1(message='Post liked successfully')


@post_router_v1.patch(
    '/posts/{post_id}/unlike/',
    status_code=200,
    response_model=PostResponseV1,
    description='Unlike a post',
)
async def unlike_post(
    post_id: UUID,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    refresh_token: str | None = request.cookies.get('refresh_token')
    post_service_v1.unlike_post(user, post_id, refresh_token, db)
    return PostResponseV1(message='Post unliked successfully')


@post_router_v1.patch(
    '/posts/{post_id}/comments/{comment_id}/like/',
    status_code=200,
    response_model=PostResponseV1,
    description='Like a comment',
)
async def like_comment(
    post_id: UUID,
    comment_id: UUID,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    refresh_token: str | None = request.cookies.get('refresh_token')
    post_service_v1.like_comment(user, post_id, comment_id, refresh_token, db)
    return PostResponseV1(message='Comment liked successfully')


@post_router_v1.patch(
    '/posts/{post_id}/comments/{comment_id}/unlike/',
    status_code=200,
    response_model=PostResponseV1,
    description='Like a comment',
)
async def unlike_comment(
    post_id: UUID,
    comment_id: UUID,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    refresh_token: str | None = request.cookies.get('refresh_token')
    post_service_v1.unlike_comment(user, post_id, comment_id, refresh_token, db)
    return PostResponseV1(message='Comment unliked successfully')


@post_router_v1.delete(
    '/posts/{post_id}/', status_code=204, description='Delete a post'
)
async def delete_post(
    post_id: UUID,
    request: Request,
    _=Depends(required_roles([UserRole.USER, UserRole.ADMIN])),
    db: Session = Depends(get_db),
):
    refresh_token: str | None = request.cookies.get('refresh_token')
    post_service_v1.delete_post(post_id, refresh_token, db)


@post_router_v1.delete(
    '/posts/{post_id}/comments/{comment_id}/',
    status_code=204,
    description='Delete comment from a post',
)
async def delete_comment(
    comment_id: UUID,
    request: Request,
    _=Depends(required_roles([UserRole.USER, UserRole.ADMIN])),
    db: Session = Depends(get_db),
):
    refresh_token: str | None = request.cookies.get('refresh_token')
    post_service_v1.delete_comment(comment_id, refresh_token, db)


@post_router_v1.delete(
    '/posts{post_id}/images/{image_url}/',
    status_code=204,
    description='Delete post image'
)
async def delete_post_image(
    post_id: UUID,
    image_url: str,
    request: Request,
    _ = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    refresh_token: str | None = request.cookies.get('refresh_token')
    post_service_v1.delete_post_image(post_id, image_url, refresh_token, db)
