from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.api.v1.classifiers.schemas import TimezoneCacheSchema
from app.db.models import Timezone
from app.db.redis import get_object_from_cache, update_object_cache


async def get_list_timezones(session: AsyncSession) -> Sequence[Timezone]:
    """Получение списка всех таймзон."""

    stmt = select(Timezone)
    result = await session.execute(stmt)
    return result.scalars().all()


async def _get_timezone_by_id_from_db(
    session: AsyncSession,
    id: int,
) -> Timezone | None:
    """Получение информации о таймзоне по id из бд."""
    stmt = select(Timezone).where(Timezone.id == id)
    result = await session.execute(stmt)
    return result.scalar()


async def get_timezone_by_id(
    session: AsyncSession, id: int, cache: bool = True
) -> Timezone | TimezoneCacheSchema | None:
    """Получение информации о таймзоне по id."""
    if cache is False:
        tz: Timezone = await _get_timezone_by_id_from_db(session, id)
        return tz

    tz_cache: TimezoneCacheSchema = await get_object_from_cache(settings.redis.timezone_prefix, id, TimezoneCacheSchema)
    if tz_cache is None:
        tz: Timezone = await _get_timezone_by_id_from_db(session, id)
        if tz is None:
            return None
        tz_cache = TimezoneCacheSchema.model_validate(tz)
        await update_object_cache(settings.redis.timezone_prefix, tz_cache)
    return tz_cache
