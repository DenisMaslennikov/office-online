import uuid
from datetime import datetime, timezone
from uuid import UUID

from fastapi import UploadFile
from pydantic import EmailStr
from sqlalchemy import Result, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.strategy_options import _AbstractLoad

from app.config import settings
from app.constants import USER_IMAGE
from app.db.models import User
from app.utils.file_utils import delete_file, save_file, validate_file_extension, validate_file_size


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
        validate_file_size(image, USER_IMAGE)
        validate_file_extension(image, USER_IMAGE)
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


async def schedule_user_deletion(session: AsyncSession, user_id: uuid.UUID) -> User:
    """Добавляет пользователя в очередь на удаление."""
    stmt = (
        update(User)
        .where(User.id == user_id)
        .values(scheduled_deletion_date=datetime.now(timezone.utc) + settings.users.user_deletion_timedelta)
        .returning(User)
        .options(joinedload(User.timezone))
    )
    result = await session.execute(stmt)
    updated_user = result.scalar_one()
    await session.commit()
    return updated_user


async def update_user_repo(
    session: AsyncSession,
    user: User,
    email: EmailStr | None = None,
    username: str | None = None,
    display_name: str | None = None,
    phone: str | None = None,
    image: UploadFile | None = None,
    timezone_id: int | None = None,
) -> User:
    """Частичное обновление информации о пользователе."""
    if email is not None:
        user.email = email
    if username is not None:
        user.username = username
    if display_name is not None:
        user.display_name = display_name
    if phone is not None:
        user.phone = phone
    if image is not None:
        validate_file_size(image, USER_IMAGE)
        validate_file_extension(image, USER_IMAGE)
        if user.image is not None:
            await delete_file(user.image, settings.files.users_images_path)
        user.image = await save_file(image, settings.files.users_images_path)
    if timezone_id is not None:
        user.timezone_id = timezone_id
    await session.commit()
    await session.refresh(user)
    return user


async def cancel_user_deletion(session: AsyncSession, user_id: uuid.UUID) -> User:
    """Отменет удаление пользователя."""
    stmt = (
        update(User)
        .where(User.id == user_id)
        .values(scheduled_deletion_date=None)
        .returning(User)
        .options(joinedload(User.timezone))
    )
    result = await session.execute(stmt)
    updated_user = result.scalar_one()
    await session.commit()
    return updated_user
