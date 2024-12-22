from datetime import datetime, timezone
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy import Result, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.strategy_options import _AbstractLoad

from app.config import settings
from app.db.models import User
from app.utils.file_utils import save_file


async def create_user_repo(
    session: AsyncSession,
    email: str,
    username: str,
    display_name: str,
    password: str,
    phone: str | None = None,
    image: UploadFile | None = None,
    timezone_id: int | None = None,
) -> User:
    """Создание нового пользователя."""
    user = User(
        email=email,
        username=username,
        display_name=display_name,
        phone=phone,
        timezone_id=timezone_id,
    )
    user.password = password
    if image is not None:
        user.image = await save_file(image, settings.files.users_images_path)
    session.add(user)
    await session.commit()
    user = await get_user_by_id_repo(session, user.id, joinedload(User.timezone))
    return user


async def get_user_by_email_repo(session: AsyncSession, email: str, *option: _AbstractLoad) -> User | None:
    """Получает пользователя по его email."""
    stmt = select(User).where(User.email == email)
    if option:
        stmt = stmt.options(*option)
    results: Result = await session.execute(stmt)
    return results.scalar()


async def get_user_by_email_or_username_repo(
    session: AsyncSession,
    email: str,
    username: str,
    *option: _AbstractLoad,
) -> User | None:
    """Получает пользователя по его email или username."""
    stmt = select(User).where(or_(User.email == email, User.username == username))
    if option:
        stmt = stmt.options(*option)
    results: Result = await session.execute(stmt)
    return results.scalars().first()


async def get_user_by_id_repo(session: AsyncSession, user_id: UUID, *option: _AbstractLoad) -> User | None:
    """Возвращает пользователя с заданным id."""
    stmt = select(User).where(User.id == user_id)
    if option:
        stmt = stmt.options(*option)
    results: Result = await session.execute(stmt)
    return results.scalar()


async def schedule_user_deletion(session: AsyncSession, user: User) -> User:
    """Добавляет пользователя в очередь на удаление."""
    user.scheduled_deletion_date = datetime.now(timezone.utc) + settings.users.user_deletion_timedelta
    await session.commit()
    return user


async def update_user_repo(session: AsyncSession, user: User, new_user_data, partial: bool = False) -> User:
    """Полное или частичное обновление информации о пользователе."""
    user_data = new_user_data.model_dump(exclude_unset=partial)
    for key, value in user_data.items():
        setattr(user, key, value)
    await session.commit()
    return user
