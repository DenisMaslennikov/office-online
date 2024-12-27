from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Timezone


async def get_list_timezones(session: AsyncSession) -> Sequence[Timezone]:
    """Получение списка всех таймзон."""

    stmt = select(Timezone)
    result = await session.execute(stmt)
    return result.scalars().all()
