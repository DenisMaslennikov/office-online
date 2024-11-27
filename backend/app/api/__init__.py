from fastapi import APIRouter

from app.api.v1 import v1_router
from app.config import settings

api_router = APIRouter()

api_router.include_router(v1_router, prefix=settings.api.v1.prefix)
