from fastapi import APIRouter  # noqa: I001
from app.api.v1.users import users_router
from app.api.v1.websocket import websocket_router

from app.config import settings as settings

v1_router = APIRouter()

v1_router.include_router(users_router, prefix=settings.api.v1.endpoints.users)
v1_router.include_router(websocket_router, prefix=settings.api.v1.endpoints.websocket)
