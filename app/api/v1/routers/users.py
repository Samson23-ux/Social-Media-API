from sqlalchemy.orm import Session
from fastapi.requests import Request
from fastapi import APIRouter, UploadFile, Depends, File

from app.models.users import User
from app.api.v1.schemas.images import ImageResponseV1
from app.api.v1.services.user_service import user_service_v1
from app.dependencies import get_db, get_current_user


users_router_v1 = APIRouter()


@users_router_v1.post(
    '/users/profile/images/upload/',
    response_model=ImageResponseV1,
    status_code=201,
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
