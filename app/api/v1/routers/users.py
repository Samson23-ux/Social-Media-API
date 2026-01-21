from sqlalchemy.orm import Session
from fastapi.requests import Request
from fastapi import APIRouter, UploadFile, Depends, File, Query

from app.models.users import User
from app.api.v1.schemas.images import ImageResponseV1
from app.dependencies import get_db, get_current_user
from app.api.v1.services.user_service import user_service_v1
from app.api.v1.schemas.posts import PostResponseV1, CommentResponseV1
from app.api.v1.schemas.users import UserResponseV1, UserUpdateV1, UserProfileResponseV1


users_router_v1 = APIRouter()


@users_router_v1.get(
    '/users/',
    status_code=200,
    response_model=list[UserResponseV1],
    description='Get a list of user profiles',
)
async def get_users(
    request: Request,
    nationality: str = Query(default=None, description='Filter by nationality'),
    year: int = Query(default=None, description='Filter by year joined'),
    sort: str = Query(
        default=None,
        description='Sort users by username, display_name, age, nationality, created_at e.g sort=age',
    ),
    order: str = Query(default=None, description='sort in asc or desc order'),
    offset: int = Query(default=0),
    limit: int = Query(default=10),
    _ = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    pass


@users_router_v1.get(
    '/users/search/',
    status_code=200,
    response_model=list[UserResponseV1],
    description='Search for user profiles',
)
async def search_users(
    request: Request,
    q: str = Query(..., description='search users by username or display_name'),
    nationality: str = Query(default=None, description='Filter by nationality'),
    year: int = Query(default=None, description='Filter by year joined'),
    sort: str = Query(
        default=None,
        description='Sort users by username, display_name, age, nationality, created_at e.g sort=age',
    ),
    order: str = Query(default=None, description='sort in asc or desc order'),
    offset: int = Query(default=0),
    limit: int = Query(default=10),
    _ = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    pass


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
    visibility: str = Query(default=None, description='Filter by visibility'),
    sort: str = Query(
        default=None,
        description='Sort users by likes, comments, created_at e.g sort=likes',
    ),
    order: str = Query(default=None, description='sort in asc or desc order'),
    offset: int = Query(default=0),
    limit: int = Query(default=10),
    _ = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    pass


@users_router_v1.get(
    '/users/{username}/',
    status_code=200,
    response_model=UserResponseV1,
    description='Get user by username',
)
async def get_user(
    username: str, _ = Depends(get_current_user), db: Session = Depends(get_db)
):
    user_read = user_service_v1.get_user_by_username(username, db)
    return UserResponseV1(message='User retrieved successfully', data=user_read)


@users_router_v1.get(
    '/users/me/profile/',
    status_code=200,
    response_model=UserProfileResponseV1,
    description='Get user profile',
)
async def get_profile(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    refresh_token = request.cookies.get('refresh_token')
    user_profile = user_service_v1.get_user_profile(user, refresh_token, db)
    return UserProfileResponseV1(
        message='User profile retrieved successfully', data=user_profile
    )


@users_router_v1.get(
    '/users/{username}/posts/{post_id}/comments/',
    status_code=200,
    response_model=CommentResponseV1,
    description='Get user post comments',
)
async def get_post_comments(
    username: str,
    request: Request,
    sort: str = Query(
        default=None, description='Sort by likes or created_at e.g sort=likes'
    ),
    order: str = Query(default=None, description='sort in asc or desc order'),
    offset: int = Query(default=0),
    limit: int = Query(default=10),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    pass


@users_router_v1.get(
    '/users/{username}}/posts/{post_id}/likes/',
    status_code=200,
    response_model=PostResponseV1,
    description='Get user post likes',
)
async def get_post_likes(
    username: str,
    request: Request,
    user_update: UserUpdateV1,
    offset: int = Query(default=0),
    limit: int = Query(default=10),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    pass


# get user followers
# get user followings
# follow a user


@users_router_v1.patch(
    '/users/me/',
    status_code=200,
    response_model=UserResponseV1,
    description='Update user profile',
)
async def update_user(
    user_update: UserUpdateV1,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    refresh_token = request.cookies.get('refresh_token')
    user_out = user_service_v1.update_user(user_update, user, refresh_token, db)
    return UserResponseV1(message='User profile updated successfully', data=user_out)


@users_router_v1.post(
    '/users/profile/images/upload/',
    status_code=201,
    response_model=ImageResponseV1,
    description='Upload user avatar and header images',
)
async def upload_image(
    request: Request,
    images: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    refresh_token = request.cookies.get('refresh_token')
    profile_images = await user_service_v1.upload_image(refresh_token, user, images, db)
    return ImageResponseV1(message='Images uploaded successfully', data=profile_images)
