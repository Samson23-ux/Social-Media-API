from sqlalchemy.orm import Session
from fastapi.requests import Request
from fastapi.responses import FileResponse
from fastapi import APIRouter, UploadFile, Depends, File, Query

from app.models.users import User
from app.dependencies import get_db, get_current_user
from app.api.v1.services.user_service import user_service_v1
from app.api.v1.schemas.images import ImageResponseV1, ImageReadV1
from app.api.v1.schemas.posts import (
    PostReadV1,
    CommentReadV1,
    PostResponseV1,
    CommentResponseV1,
)
from app.api.v1.schemas.users import (
    UserReadV1,
    UserUpdateV1,
    UserProfileV1,
    UserResponseV1,
    UserProfileResponseV1,
)


users_router_v1 = APIRouter()


@users_router_v1.get(
    '/users/',
    status_code=200,
    response_model=UserResponseV1,
    description='Get a list of user profiles',
)
async def get_users(
    request: Request,
    nationality: str = Query(default=None, description='Filter by nationality'),
    year: int = Query(default=None, description='Filter by year joined'),
    sort: str = Query(
        default=None,
        description='Sort users by username, display_name, nationality, created_at',
    ),
    order: str = Query(default=None, description='Sort in asc or desc order'),
    offset: int = Query(default=0),
    limit: int = Query(default=10),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    refresh_token: str | None = request.cookies.get('refresh_token')
    users: list[UserReadV1] = user_service_v1.get_users(
        user, db, refresh_token, nationality, year, sort, order, offset, limit
    )
    return UserResponseV1(message='Users retrieved successfully', data=users)


@users_router_v1.get(
    '/users/search/',
    status_code=200,
    response_model=UserResponseV1,
    description='Search for user profiles',
)
async def search_users(
    request: Request,
    q: str = Query(..., description='Search users by username or display_name'),
    nationality: str = Query(default=None, description='Filter by nationality'),
    year: int = Query(default=None, description='Filter by year joined'),
    sort: str = Query(
        default=None,
        description='Sort users by username, display_name, nationality, created_at',
    ),
    order: str = Query(default=None, description='Sort in asc or desc order'),
    offset: int = Query(default=0),
    limit: int = Query(default=10),
    _=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    refresh_token: str | None = request.cookies.get('refresh_token')
    users: list[UserReadV1] = user_service_v1.search_users(
        db, refresh_token, q, nationality, year, sort, order, offset, limit
    )
    return UserResponseV1(message='Searched users retrieved successfully', data=users)


@users_router_v1.get(
    '/users/{username}/posts/',
    status_code=200,
    description='Get user posts',
    response_model=PostResponseV1,
)
async def get_user_posts(
    request: Request,
    username: str,
    created_at: int = Query(default=None, description='Filter by year created'),
    sort: str = Query(
        default=None,
        description='Sort posts by likes, comments, created_at',
    ),
    order: str = Query(default=None, description='Sort in asc or desc order'),
    offset: int = Query(default=0),
    limit: int = Query(default=10),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    refresh_token: str | None = request.cookies.get('refresh_token')
    user_posts: list[PostReadV1] = user_service_v1.get_user_posts(
        user, username, refresh_token, db, created_at, sort, order, offset, limit
    )
    return PostResponseV1(message='Posts retrieved successfully', data=user_posts)


@users_router_v1.get(
    '/users/{username}/profile/',
    status_code=200,
    response_model=UserResponseV1,
    description='Get user profile by username',
)
async def get_user(
    request: Request,
    username: str,
    _=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    refresh_token: str | None = request.cookies.get('refresh_token')
    user_read: User = user_service_v1.get_user_profile(username, refresh_token, db)
    return UserResponseV1(message='User retrieved successfully', data=user_read)


@users_router_v1.get(
    '/users/me/profile/',
    status_code=200,
    response_model=UserProfileResponseV1,
    description='Get current user profile',
)
async def get_profile(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    refresh_token: str | None = request.cookies.get('refresh_token')
    user_profile: UserProfileV1 = user_service_v1.get_current_user_profile(
        user, refresh_token, db
    )
    return UserProfileResponseV1(
        message='User profile retrieved successfully', data=user_profile
    )


@users_router_v1.get(
    '/users/{username}/followers/',
    status_code=200,
    response_model=UserResponseV1,
    description='Get user followers',
)
async def get_followers(
    username: str,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    refresh_token: str | None = request.cookies.get('refresh_token')
    followers: list[User] = user_service_v1.get_followers(
        user, username, refresh_token, db
    )
    return UserResponseV1(
        message='User followers retrieved successfully', data=followers
    )


@users_router_v1.get(
    '/users/{username}/followings/',
    status_code=200,
    response_model=UserResponseV1,
    description='Get user followers',
)
async def get_followings(
    username: str,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    refresh_token: str | None = request.cookies.get('refresh_token')
    followings: list[User] = user_service_v1.get_followings(
        user, username, refresh_token, db
    )
    return UserResponseV1(
        message='User followings retrieved successfully', data=followings
    )


@users_router_v1.get(
    '/users/{username}/posts/comments/',
    status_code=200,
    response_model=CommentResponseV1,
    description='Get user comments',
)
async def get_user_comments(
    username: str,
    request: Request,
    created_at: int = Query(default=None, description='Filter by year created'),
    sort: str = Query(
        default=None,
        description='Sort comments by likes and created_at',
    ),
    order: str = Query(default=None, description='Sort in asc or desc order'),
    offset: int = Query(default=0),
    limit: int = Query(default=10),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    refresh_token: str | None = request.cookies.get('refresh_token')
    comments: list[CommentReadV1] = user_service_v1.get_user_comments(
        user, username, refresh_token, db, created_at, sort, order, offset, limit
    )
    return CommentResponseV1(
        message='User comments retrieved successfully', data=comments
    )


@users_router_v1.get(
    '/users/{username}/posts/likes/',
    status_code=200,
    response_model=PostResponseV1,
    description='Get user comments',
)
async def get_liked_posts(
    username: str,
    request: Request,
    offset: int = Query(default=0),
    limit: int = Query(default=10),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    refresh_token: str | None = request.cookies.get('refresh_token')
    posts: list[PostReadV1] = user_service_v1.get_liked_post(
        user, username, refresh_token, db, offset, limit
    )
    return PostResponseV1(message='User liked posts retrived successflly', data=posts)


@users_router_v1.get(
    '/users/{username}/profile/images/{image_url}/',
    status_code=200,
    response_class=FileResponse,
    description='Get user profile image',
)
async def get_user_avatar(
    username: str,
    image_url: str,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    refresh_token: str | None = request.cookies.get('refresh_token')
    avatar: bytes = await user_service_v1.get_user_avatar(
        user, username, refresh_token, image_url, db
    )
    return FileResponse(path=avatar)


@users_router_v1.post(
    '/users/profile/images/',
    status_code=201,
    response_model=ImageResponseV1,
    description='Upload user avatar and header images',
)
async def upload_image(
    request: Request,
    images: list[UploadFile] = File(
        ..., description='Upload at least 0 and at most 2 avatar'
    ),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    refresh_token: str | None = request.cookies.get('refresh_token')
    profile_images: ImageReadV1 = await user_service_v1.upload_image(
        refresh_token, user, images, db
    )
    return ImageResponseV1(message='Images uploaded successfully', data=profile_images)


@users_router_v1.patch(
    '/users/me/',
    status_code=200,
    response_model=UserResponseV1,
    description='Update user profile',
)
async def update_user(
    request: Request,
    user_update: UserUpdateV1,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    refresh_token: str | None = request.cookies.get('refresh_token')
    user_out: User = user_service_v1.update_user(user_update, user, refresh_token, db)
    return UserResponseV1(message='User profile updated successfully', data=user_out)


@users_router_v1.patch(
    '/users/{username}/follow/',
    status_code=200,
    response_model=UserResponseV1,
    description='Follow a user',
)
async def follow_user(
    username: str,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    refresh_token: str | None = request.cookies.get('refresh_token')
    user_service_v1.follow_user(user, username, refresh_token, db)
    return UserResponseV1(message='User followed successfully')


@users_router_v1.patch(
    '/users/{username}/unfollow/',
    status_code=200,
    response_model=UserResponseV1,
    description='Unfollow a user',
)
async def unfollow_user(
    username: str,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    refresh_token: str | None = request.cookies.get('refresh_token')
    user_service_v1.unfollow_user(user, username, refresh_token, db)
    return UserResponseV1(message='User unfollowed successfully')


@users_router_v1.delete(
    '/users/profile/images/{image_url}/',
    status_code=204,
    description='Delete user profile image',
)
async def delete_profile_image(
    image_url: str,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    refresh_token: str | None = request.cookies.get('refresh_token')
    user_service_v1.delete_profile_image(user, image_url, refresh_token, db)
    
