from fastapi import FastAPI

from app.core.config import settings
from app.api.v1.routers.auth import auth_router_v1
from app.api.v1.routers.users import users_router_v1

app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
)

from app.core import exception_handlers

app.include_router(auth_router_v1, prefix=settings.API_VERSION_PREFIX, tags=['Auth'])
app.include_router(users_router_v1, prefix=settings.API_VERSION_PREFIX, tags=['Users'])
