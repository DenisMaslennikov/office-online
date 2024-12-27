from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.classifiers.crud import get_timezone_by_id
from app.api.v1.users.schemas import UserCacheSchema, UserReadTZSchema


async def add_tz_to_user(user: UserCacheSchema, session: AsyncSession) -> UserReadTZSchema:
    """Получает информацию о таймзоне для объекта UserCacheSchema и преобразует его в UserReadTZSchema."""
    return UserReadTZSchema(**(user.model_dump() | {"timezone": await get_timezone_by_id(session, user.timezone_id)}))
