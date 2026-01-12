from sqlalchemy.orm import Session
from fastapi.requests import Request
from fastapi.responses import Response
from fastapi import APIRouter, Depends, Form
from fastapi.security import OAuth2PasswordRequestForm

from app.models.users import User
from app.core.config import settings
from app.dependencies import get_db, get_current_user
from app.api.v1.services.auth_service import auth_service_v1
from app.api.v1.schemas.users import UserCreateV1, UserResponseV1
from app.api.v1.schemas.auth import TokenV1, BaseResponseV1


auth_router_v1 = APIRouter()


@auth_router_v1.post(
    '/auth/sign-up/',
    status_code=201,
    response_model=UserResponseV1,
    description='Create user account',
)
async def sign_up(user_create: UserCreateV1, db: Session = Depends(get_db)):
    user = auth_service_v1.sign_up(user_create, db)
    print(user.email)
    return UserResponseV1(message='User created successfully', data=user)


@auth_router_v1.post(
    '/auth/sign-in/',
    status_code=201,
    response_model=TokenV1,
    description='User login with credentials validation',
)
async def sign_in(
    response: Response,
    login_form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    access_token, refresh_token = auth_service_v1.sign_in(
        login_form.username, login_form.password, db
    )
    response.set_cookie(
        key='refresh_token',
        value=refresh_token,
        httponly=True,
        secure=settings.ENVIROMENT == 'production',
        samesite='lax',
    )
    return access_token


@auth_router_v1.get(
    '/auth/refresh/',
    status_code=200,
    response_model=TokenV1,
    description='Request for new access token',
)
async def get_access_token(
    response: Response,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    refresh_token = request.cookies.get('refresh_token')
    access_token, new_refresh_token = auth_service_v1.create_access_token(
        refresh_token, db
    )
    response.set_cookie(
        key='refresh_token',
        value=new_refresh_token,
        httponly=True,
        secure=settings.ENVIROMENT == 'production',
        samesite='lax',
    )
    return access_token


@auth_router_v1.patch(
    '/auth/sign-out/',
    status_code=200,
    response_model=BaseResponseV1,
    description='Sign out user',
)
async def sign_out(
    request: Request,
    _=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    refresh_token = request.cookies.get('refresh_token')
    auth_service_v1.sign_out(refresh_token, db)
    return BaseResponseV1(message='Sign out succesful')


@auth_router_v1.patch(
    '/auth/update-password/',
    status_code=200,
    response_model=UserResponseV1,
    description='Update password with validation of current password',
)
async def update_password(
    request: Request,
    curr_password: str = Form(..., min_length=8),
    new_password: str = Form(..., min_length=8),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    refresh_token = request.cookies.get('refresh_token')
    user = auth_service_v1.update_password(
        refresh_token, curr_password, new_password, user, db
    )
    return UserResponseV1(message='Password updated successfully', data=user)


@auth_router_v1.patch(
    '/auth/reset-password/',
    status_code=200,
    response_model=UserResponseV1,
    description='Reset password if forgotten or lost',
)
async def reset_password(
    email: str = Form(...),
    new_password: str = Form(..., min_length=8),
    db: Session = Depends(get_db),
):
    user = auth_service_v1.reset_password(email, new_password, db)
    return UserResponseV1(message='Password reset successful', data=user)


@auth_router_v1.patch(
    '/auth/restore-account/',
    status_code=200,
    response_model=UserResponseV1,
    description='Restore account after temporary deletion before 30 days',
)
async def restore_account(
    email: str = Form(...),
    account_password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = auth_service_v1.restore_account(email, account_password, db)
    return UserResponseV1(message='Account restored successfully', data=user)


@auth_router_v1.delete(
    '/auth/delete-account/', status_code=200, description='Delete account temporarily'
)
async def delete_account(
    request: Request,
    password: str = Form(),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    refresh_token = request.cookies.get('refresh_token')
    auth_service_v1.delete_account(refresh_token, password, user, db)
    return UserResponseV1(message='User account deleted successfully')
