import sentry_sdk
from fastapi import FastAPI
from fastapi.requests import Request
from datetime import datetime, timezone
from sentry_sdk import logger as sentry_logger

from app.core.config import settings
from app.api.v1.routers.auth import auth_router_v1
from app.api.v1.routers.users import users_router_v1

sentry_sdk.init(
    # sdk dsn
    dsn=settings.SENTRY_SDK_DSN,

    # allow collection of personal identifiable information
    # read more at https://docs.sentry.io/platforms/python/data-management/data-collected/
    send_default_pii=True,

    # enable logs
    enable_logs=True,

    # traces 100%, adjust to reduce code trace rate
    traces_sample_rate=1.0,

    # tracks function call stack for possible code optimization
    profile_session_sample_rate=1.0,

    # profile lifecycle controlled automatically
    # change to manual for more control on start and stop time
    profile_lifecycle='trace' 
)


app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
)

from app.core import exception_handlers

app.include_router(auth_router_v1, prefix=settings.API_VERSION_PREFIX, tags=['Auth'])
app.include_router(users_router_v1, prefix=settings.API_VERSION_PREFIX, tags=['Users'])
app.include_router(users_router_v1, prefix=settings.API_VERSION_PREFIX, tags=['Posts'])


# check api health status
@app.get('/health', status_code=200)
async def check_health():
    return {'message': 'OK'}


@app.middleware('http')
async def log_middleware(request: Request, call_next):
    log_message = f'{datetime.now(timezone.utc)} {request.method} {request.url}'
    sentry_logger.info(log_message)
    response = await call_next(request)
    response.headers['X-App-Name'] = 'Social Media API'
    return response
