from fastapi import APIRouter, Depends

from app.dependencies import get_current_user, get_db, required_roles


post_router_v1 = APIRouter()

# get comment
# get post comments