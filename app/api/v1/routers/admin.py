from sqlalchemy.orm import Session
from fastapi.requests import Request
from fastapi import APIRouter, Depends


from app.models.users import User
from app.dependencies import get_db, required_roles
from app.api.v1.services.admin_service import admin_service_v1
from app.api.v1.schemas.admin import UserCountV1, UserCountResponse
from app.api.v1.schemas.users import UserRole, UserResponseV1, UserReadV1


admin_router_v1 = APIRouter()


@admin_router_v1.get(
    '/admin/users/suspended/',
    status_code=200,
    response_model=UserResponseV1,
    description='Get suspended users'
)
async def get_suspended_users(
    request: Request,
    admin_user: User = Depends(required_roles([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    refresh_token: str | None = request.cookies.get('refresh_token')
    users: list[UserReadV1] = admin_service_v1.get_suspended_users(
        admin_user, refresh_token, db
    )
    return UserResponseV1(
        message='Total suspended users retrieved successfully', data=users
    )


@admin_router_v1.get(
    '/admin/users/all/',
    status_code=200,
    response_model=UserCountResponse,
    description='Get total active users'
)
async def get_total_active_users(
    request: Request,
    admin_user: User = Depends(required_roles([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    refresh_token: str | None = request.cookies.get('refresh_token')
    users: UserCountV1 = admin_service_v1.get_all_active_users(
        admin_user, refresh_token, db
    )
    return UserCountResponse(
        message='Total active users retrieved successfully', data=users
    )


@admin_router_v1.patch(
    '/admin/users/{username}/assign-admin-role/',
    status_code=200,
    response_model=UserResponseV1,
    description='Assign admin role to users'
)
async def assign_admin(
    request: Request,
    username: str,
    admin_user: User = Depends(required_roles([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    refresh_token: str | None = request.cookies.get('refresh_token')
    user: UserReadV1 = admin_service_v1.assign_admin_role(
        admin_user, username, refresh_token, db
    )
    return UserResponseV1(
        message='User role updated successfully', data=user
    )


@admin_router_v1.patch(
    '/admin/users/{username}/suspend/',
    status_code=200,
    response_model=UserResponseV1,
    description='Suspend users'
)
async def suspend_user(
    request: Request,
    username: str,
    admin_user: User = Depends(required_roles([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    refresh_token: str | None = request.cookies.get('refresh_token')
    user: UserReadV1 = admin_service_v1.suspend_user(
        admin_user, username, refresh_token, db
    )
    return UserResponseV1(
        message='User suspended successfully', data=user
    )


@admin_router_v1.patch(
    '/admin/users/{username}/unsuspend/',
    status_code=200,
    response_model=UserResponseV1,
    description='Unsuspend users'
)
async def unsuspend_user(
    request: Request,
    username: str,
    admin_user: User = Depends(required_roles([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    refresh_token: str | None = request.cookies.get('refresh_token')
    user: UserReadV1 = admin_service_v1.unsuspend_user(
        admin_user, username, refresh_token, db
    )
    return UserResponseV1(
        message='User unsuspended successfully', data=user
    )
